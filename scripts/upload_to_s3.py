import os
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME is missing from .env")

if not DATA_DIR.is_dir():
    raise FileNotFoundError(f"Dataset directory not found: {DATA_DIR}")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(
        retries={"max_attempts": 10, "mode": "standard"},
        connect_timeout=30,
        read_timeout=120,
    ),
)

transfer_config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    multipart_chunksize=8 * 1024 * 1024,
    max_concurrency=2,
)


def upload_file(file_path: Path) -> None:
    key = f"raw/{file_path.name}"
    size_mb = file_path.stat().st_size / (1024 * 1024)

    print(f"\nUploading {file_path.name} ({size_mb:.2f} MB)...")

    s3.upload_file(
        str(file_path),
        BUCKET_NAME,
        key,
        ExtraArgs={"ServerSideEncryption": "AES256"},
        Config=transfer_config,
    )

    result = s3.head_object(Bucket=BUCKET_NAME, Key=key)

    if result["ContentLength"] != file_path.stat().st_size:
        raise RuntimeError(f"Size mismatch for {file_path.name}")

    print(f"Verified: s3://{BUCKET_NAME}/{key}")


def main() -> None:
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    # Hold users.csv back until its sensitive fields are reviewed.
    already_uploaded = {
    "food.csv",
    "menu.csv",
    "order_items.csv",
    "restaurant.csv",
    "reviews.csv"
}

    selected_files = [
        path for path in csv_files
        if path.name.lower() not in already_uploaded
    
    ]

    if not selected_files:
        raise FileNotFoundError(f"No eligible CSV files found in {DATA_DIR}")

    print(f"Bucket: {BUCKET_NAME}")
    print(f"Region: {AWS_REGION}")
    print(f"Files selected: {len(selected_files)}")

    for path in selected_files:
        try:
            upload_file(path)
        except (ClientError, OSError, RuntimeError) as exc:
            print(f"Upload failed for {path.name}: {exc}")
            raise

    print("\nAll selected files uploaded and verified.")


if __name__ == "__main__":
    main()
