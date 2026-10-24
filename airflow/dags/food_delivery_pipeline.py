
from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


DBT = "/opt/airflow/dbt-venv/bin/dbt"
PYTHON = "/opt/airflow/dbt-venv/bin/python"
PROJECT = "/opt/airflow/project"

with DAG(
    dag_id="food_delivery_data_pipeline",
    description="Orchestrate Snowflake ingestion and dbt analytics",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "ashwin",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["food-delivery", "data-engineering"],
) as dag:

    check_environment = BashOperator(
        task_id="check_pipeline_environment",
        bash_command=r"""
            missing=0
            for key in \
              SNOWFLAKE_ACCOUNT \
              SNOWFLAKE_USER \
              SNOWFLAKE_PASSWORD \
              SNOWFLAKE_ROLE \
              SNOWFLAKE_WAREHOUSE \
              SNOWFLAKE_DATABASE \
              SNOWFLAKE_SCHEMA
            do
                if [ -z "$(printenv "$key" || true)" ]; then
                    echo "Missing required variable: $key"
                    missing=1
                fi
            done

            if [ "$missing" -ne 0 ]; then
                exit 1
            fi

            echo "All required Snowflake variables are present."
        """,
        do_xcom_push=False,
    )

    validate_stage = BashOperator(
        task_id="validate_snowflake_stage",
        bash_command=(
            f"{PYTHON} "
            f"{PROJECT}/scripts/check_snowflake_stage.py"
        ),
        do_xcom_push=False,
    )

    load_raw_data = BashOperator(
        task_id="load_snowflake_raw_tables",
        bash_command=(
            f"{PYTHON} "
            f"{PROJECT}/scripts/execute_sql.py "
            f"{PROJECT}/sql/load_raw_data.sql"
        ),
        do_xcom_push=False,
    )

    build_dbt_models = BashOperator(
        task_id="build_dbt_models_and_tests",
        bash_command=(
            f"cd {PROJECT}/food_delivery_dbt && "
            f"{DBT} build "
            "--profiles-dir /opt/airflow/dbt_profiles"
        ),
        do_xcom_push=False,
    )

    (
        check_environment
        >> validate_stage
        >> load_raw_data
        >> build_dbt_models
    )
