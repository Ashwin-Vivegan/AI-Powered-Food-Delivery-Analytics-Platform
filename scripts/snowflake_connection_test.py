
import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from the project root .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

required_vars = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_ROLE",
]

missing = [name for name in required_vars if not os.getenv(name)]
if missing:
    raise SystemExit(
        f"Missing environment variables in .env: {', '.join(missing)}"
    )

connection = None

try:
    connection = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        role=os.environ["SNOWFLAKE_ROLE"],
        login_timeout=30,
        network_timeout=30,
    )

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                CURRENT_ACCOUNT(),
                CURRENT_USER(),
                CURRENT_ROLE(),
                CURRENT_WAREHOUSE(),
                CURRENT_DATABASE(),
                CURRENT_SCHEMA()
        """)

        result = cursor.fetchone()
        print("Snowflake connection successful!")
        print(f"Account:   {result[0]}")
        print(f"User:      {result[1]}")
        print(f"Role:      {result[2]}")
        print(f"Warehouse: {result[3]}")
        print(f"Database:  {result[4]}")
        print(f"Schema:    {result[5]}")

except snowflake.connector.errors.Error as error:
    print(f"Snowflake connection failed: {error}")
    raise SystemExit(1)

finally:
    if connection is not None:
        connection.close()
