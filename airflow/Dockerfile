FROM apache/airflow:3.3.2

RUN python -m venv /opt/airflow/dbt-venv \
    && /opt/airflow/dbt-venv/bin/pip install --no-cache-dir \
        "dbt-core==1.12.6" \
        "dbt-snowflake==1.12.4" \
        "jsonschema==4.26.0" \
        "referencing==0.37.0" \
        boto3 \
        snowflake-connector-python \
        python-dotenv
