
import json
import os
import time
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILE_PATH = PROJECT_ROOT / "data" / "raw" / "order_items.csv"
STATE_PATH = FILE_PATH.parent / ".order_items_upload_state.json"

load_dotenv(PROJECT_ROOT / ".env")

BUCKET = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("AWS_REGION", "ap-south-1")
KEY = f"raw/{FILE_PATH.name}"

# Smaller parts are more practical on unstable connections.
PART_SIZE = 8 * 1024 * 1024
MAX_PART_RETRIES = 8

if not BUCKET:
    raise ValueError("S3_BUCKET_NAME is missing from .env")

if not FILE_PATH.is_file():
    raise FileNotFoundError(FILE_PATH)

s3 = boto3.client(
    "s3",
    region_name=REGION,
    config=Config(
        retries={"max_attempts": 8, "mode": "standard"},
        connect_timeout=30,
        read_timeout=180,
    ),
)


def save_state(state):
    temporary = STATE_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2))
    temporary.replace(STATE_PATH)


def list_uploaded_parts(upload_id):
    parts = {}
    marker = 0

    while True:
        response = s3.list_parts(
            Bucket=BUCKET,
            Key=KEY,
            UploadId=upload_id,
            PartNumberMarker=marker,
        )

        for part in response.get("Parts", []):
            parts[part["PartNumber"]] = part["ETag"]

        if not response.get("IsTruncated"):
            break

        marker = response["NextPartNumberMarker"]

    return parts


def main():
    file_size = FILE_PATH.stat().st_size
    part_count = (file_size + PART_SIZE - 1) // PART_SIZE

    state = None

    if STATE_PATH.exists():
        try:
            candidate = json.loads(STATE_PATH.read_text())

            if (
                candidate["bucket"] == BUCKET
                and candidate["key"] == KEY
                and candidate["file_size"] == file_size
                and candidate["file_mtime"] == FILE_PATH.stat().st_mtime
            ):
                # Check whether the saved multipart upload still exists.
                list_uploaded_parts(candidate["upload_id"])
                state = candidate
                print("Resuming previous multipart upload...")
        except (ClientError, BotoCoreError, OSError, ValueError, KeyError):
            print("Saved upload could not be resumed; starting a new upload.")

    if state is None:
        response = s3.create_multipart_upload(
            Bucket=BUCKET,
            Key=KEY,
            ServerSideEncryption="AES256",
        )

        state = {
            "bucket": BUCKET,
            "key": KEY,
            "file_size": file_size,
            "file_mtime": FILE_PATH.stat().st_mtime,
            "upload_id": response["UploadId"],
        }
        save_state(state)
        completed = {}
        print("Started a new multipart upload.")
    else:
        completed = list_uploaded_parts(state["upload_id"])

    upload_id = state["upload_id"]
    transferred = sum(
        min(PART_SIZE, file_size - (number - 1) * PART_SIZE)
        for number in completed
    )

    try:
        with FILE_PATH.open("rb") as file:
            for part_number in range(1, part_count + 1):
                if part_number in completed:
                    continue

                offset = (part_number - 1) * PART_SIZE
                file.seek(offset)
                chunk = file.read(min(PART_SIZE, file_size - offset))

                for attempt in range(1, MAX_PART_RETRIES + 1):
                    try:
                        response = s3.upload_part(
                            Bucket=BUCKET,
                            Key=KEY,
                            UploadId=upload_id,
                            PartNumber=part_number,
                            Body=chunk,
                        )

                        completed[part_number] = response["ETag"]
                        save_state(state)
                        transferred += len(chunk)

                        percent = transferred / file_size * 100
                        print(
                            f"\rProgress: {percent:6.2f}% "
                            f"({transferred / (1024**2):.1f} / "
                            f"{file_size / (1024**2):.1f} MiB)",
                            end="",
                            flush=True,
                        )
                        break

                    except (BotoCoreError, ClientError, OSError):
                        if attempt == MAX_PART_RETRIES:
                            raise

                        wait = min(2 ** attempt, 60)
                        print(
                            f"\nPart {part_number} failed. "
                            f"Retry {attempt}/{MAX_PART_RETRIES - 1} "
                            f"in {wait}s..."
                        )
                        time.sleep(wait)

        print("\nCompleting multipart upload...")

        parts = [
            {"PartNumber": number, "ETag": completed[number]}
            for number in sorted(completed)
        ]

        s3.complete_multipart_upload(
            Bucket=BUCKET,
            Key=KEY,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )

        result = s3.head_object(Bucket=BUCKET, Key=KEY)

        if result["ContentLength"] != file_size:
            raise RuntimeError("Uploaded file size does not match local file.")

        STATE_PATH.unlink(missing_ok=True)
        print(f"Verified: s3://{BUCKET}/{KEY}")

    except Exception:
        print(
            "\nUpload paused or failed. Keep the local CSV and state file. "
            "Run this script again to resume completed parts."
        )
        raise


if __name__ == "__main__":
    main()
