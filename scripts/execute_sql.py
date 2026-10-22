
import os
import sys
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

# Resolve project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = (
    PROJECT_ROOT / sys.argv[1]
    if len(sys.argv) > 1
    else PROJECT_ROOT / "sql" / "create_raw_tables.sql"
)

# Load environment variables from project root
load_dotenv(PROJECT_ROOT / ".env")


def main():
    if not SQL_FILE.exists():
        print(f"SQL file not found: {SQL_FILE}")
        sys.exit(1)

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
        print(f"Missing .env variables: {', '.join(missing)}")
        sys.exit(1)

    sql_text = SQL_FILE.read_text(encoding="utf-8")

    # Split statements because this file contains multiple CREATE TABLE commands.
    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]

    if not statements:
        print("No SQL statements found.")
        sys.exit(1)

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
            network_timeout=60,
        )

        print("Connected to Snowflake.")

        with connection.cursor() as cursor:
            for index, statement in enumerate(statements, start=1):
                # Display only the first line, not potentially sensitive SQL.
                description = statement.splitlines()[0][:100]
                print(f"[{index}/{len(statements)}] Executing: {description}")

                cursor.execute(statement)
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()

                    if rows:
                        print("    Snowflake result:")
                        for row in rows:
                            result = dict(zip(columns, row))
                            print(f"    {result}")
                    else:
                        print("    Statement executed successfully; no result rows returned.")
                else:
                    print("    Statement executed successfully.")

        print(f"\nCompleted successfully: {len(statements)} SQL statements.")

    except snowflake.connector.errors.Error as error:
        print(f"\nSnowflake execution failed: {error}")
        sys.exit(1)

    finally:
        if connection is not None:
            connection.close()
            print("Snowflake connection closed.")


if __name__ == "__main__":
    main()
