
import os
import sys

import snowflake.connector
from dotenv import load_dotenv

# Environment variables are supplied by the Airflow worker.
# Loading a local .env is optional and must not override them.
load_dotenv(override=False)

REQUIRED_ENV = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
]

missing_env = [key for key in REQUIRED_ENV if not os.getenv(key)]
if missing_env:
    sys.exit(
        "Missing required environment variables: "
        + ", ".join(missing_env)
    )

expected_files = {
    "food.csv",
    "menu.csv",
    "order_items.csv",
    "restaurant.csv",
    "reviews.csv",
    "users.csv",
}

connection = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    database="FOOD_DELIVERY_DB",
    schema="RAW",
)

try:
    with connection.cursor() as cursor:
        cursor.execute(
            "LIST @FOOD_DELIVERY_DB.RAW.FOOD_S3_STAGE"
        )
        rows = cursor.fetchall()

    available_files = {
        str(row[0]).replace("\\", "/").rsplit("/", 1)[-1].lower()
        for row in rows
    }

    found = expected_files & available_files
    missing = expected_files - available_files

    print(f"Expected files: {len(expected_files)}")
    print(f"Files found: {len(found)}")
    print("Found:", ", ".join(sorted(found)))

    if missing:
        sys.exit(
            "Stage validation failed. Missing: "
            + ", ".join(sorted(missing))
        )

    print("SUCCESS: All six expected CSV files are available.")

finally:
    connection.close()
