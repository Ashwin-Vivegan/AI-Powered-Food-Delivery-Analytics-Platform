
from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="food_delivery_pipeline_smoke_test",
    description="Verify Airflow can discover and execute project workflows",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "ashwin",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["food-delivery", "milestone-5", "smoke-test"],
) as dag:

    start = BashOperator(
        task_id="start_pipeline",
        bash_command="echo 'Food delivery pipeline starting'",
        do_xcom_push=False,
    )

    verify_runtime = BashOperator(
    task_id="verify_airflow_runtime",
    bash_command="python --version && echo 'Airflow task runtime is operational'",
    do_xcom_push=False,
)

    finish = BashOperator(
        task_id="finish_pipeline",
        bash_command="echo 'Airflow workflow completed successfully'",
        do_xcom_push=False,
    )

    start >> verify_runtime >> finish
