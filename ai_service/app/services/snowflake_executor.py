
import json
import os
from typing import Any

import snowflake.connector

from app.services.sql_generator import validate_sql


EXPECTED_ROLE = "AI_ANALYTICS_READONLY"
MAX_ROWS = 100
QUERY_TIMEOUT_SECONDS = 30


def _connect_readonly():
    required = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "SNOWFLAKE_AI_ROLE",
    ]

    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(
            "Missing Snowflake settings: " + ", ".join(missing)
        )

    role = os.environ["SNOWFLAKE_AI_ROLE"]

    # Never fall back to the administrative role.
    if role.upper() != EXPECTED_ROLE:
        raise PermissionError(
            f"AI queries require the {EXPECTED_ROLE} role."
        )

    connection = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=EXPECTED_ROLE,
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        session_parameters={
            "STATEMENT_TIMEOUT_IN_SECONDS": QUERY_TIMEOUT_SECONDS,
            "QUERY_TAG": "AI_FOOD_DELIVERY_TEXT_TO_SQL",
        },
        client_session_keep_alive=False,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()"
            )
            current_role, current_database, current_schema = (
                cursor.fetchone()
            )

        if (current_role or "").upper() != EXPECTED_ROLE:
            raise PermissionError(
                "Snowflake did not activate the required read-only role."
            )

        expected_database = os.environ["SNOWFLAKE_DATABASE"].upper()
        expected_schema = os.environ["SNOWFLAKE_SCHEMA"].upper()

        if (current_database or "").upper() != expected_database:
            raise PermissionError("Unexpected Snowflake database.")

        if (current_schema or "").upper() != expected_schema:
            raise PermissionError("Unexpected Snowflake schema.")

        return connection

    except Exception:
        connection.close()
        raise


def verify_readonly_connection() -> dict[str, str]:
    """Verify the active Snowflake role and session context."""
    connection = _connect_readonly()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()"
            )
            role, database, schema = cursor.fetchone()

        return {
            "role": role,
            "database": database,
            "schema": schema,
            "status": "connected",
        }
    finally:
        connection.close()


def execute_readonly_query(
    sql: str,
    target_mart: str,
) -> dict[str, Any]:
    """Validate and execute a read-only query against an approved mart."""

    # Validate again immediately before database execution.
    safe_sql = validate_sql(sql, target_mart)

    connection = _connect_readonly()

    try:
        with connection.cursor() as cursor:
            cursor.execute(safe_sql, timeout=QUERY_TIMEOUT_SECONDS)

            columns = (
                [description[0] for description in cursor.description]
                if cursor.description
                else []
            )

            fetched_rows = cursor.fetchmany(MAX_ROWS + 1)

            if len(fetched_rows) > MAX_ROWS:
                raise RuntimeError(
                    "Query exceeded the permitted result size."
                )

            result_rows = [
                dict(zip(columns, row))
                for row in fetched_rows
            ]

            # Convert Snowflake decimals and date/time values into
            # JSON-compatible strings without losing numeric precision.
            serializable_rows = json.loads(
                json.dumps(result_rows, default=str)
            )

            return {
                "columns": columns,
                "rows": serializable_rows,
                "row_count": len(serializable_rows),
            }

    finally:
        connection.close()
