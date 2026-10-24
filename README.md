# AI-Powered Food Delivery Analytics Platform

An end-to-end data engineering and AI analytics platform that transforms food delivery data into analytics-ready datasets using AWS S3, Snowflake, dbt, and Apache Airflow. The project implements cloud data ingestion, warehouse transformations, data-quality testing, and workflow orchestration, with planned extensions for LLM-powered analytics and natural-language querying.

## Project Overview

Food delivery platforms generate large volumes of data about restaurants, menus, food items, orders, users, and customer reviews. This project builds a data pipeline that ingests raw datasets, loads them into a cloud data warehouse, transforms them into useful analytical models, and orchestrates the workflow using Apache Airflow.

The current implementation includes:
- AWS S3 for raw data storage.
- Snowflake for cloud data warehousing and RAW-layer ingestion.
- dbt Core for SQL-based transformations, intermediate models, analytics marts, and data-quality tests.
- Apache Airflow for orchestrating the ingestion and transformation workflow.
- Docker Compose for running Airflow locally.

The next stage will introduce an LLM-powered analytics interface, followed by a Streamlit application and production deployment.

## Architecture

### Implemented architecture

```text
Source CSV Datasets
        |
        v
   Python / boto3
        |
        v
      AWS S3
        |
        v
Snowflake Storage Integration
        |
        v
 Snowflake External Stage
        |
        v
  Snowflake RAW Tables
        |
        v
     dbt Core
        |
        +--> Staging Models
        |
        +--> Intermediate Model
        |
        +--> Analytics Marts
        |
        v
   Data-Quality Tests
```

Apache Airflow orchestrates the workflow by validating the Snowflake stage, executing the RAW data-loading SQL, and running `dbt build`.

### Target architecture

```text
AWS S3
   |
   v
Snowflake RAW Layer
   |
   v
dbt Staging, Intermediate Models and Marts
   |
   v
Apache Airflow Orchestration
   |
   v
LLM Analytics
   |
   +--> Retrieval-Augmented Generation (RAG)
   |
   +--> Text-to-SQL
   |
   v
Streamlit Application
   |
   v
Production Deployment and Monitoring
```

The AI, user interface, and production deployment components are planned extensions and are not yet implemented.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming language | Python |
| Cloud storage | Amazon S3 |
| Data warehouse | Snowflake |
| Data ingestion | Snowflake external stage, `COPY INTO`, Python |
| Data transformation | dbt Core, SQL |
| Warehouse adapter | dbt-snowflake |
| Workflow orchestration | Apache Airflow |
| Containerization | Docker, Docker Compose, WSL2 |
| Airflow services | PostgreSQL, Redis, CeleryExecutor |
| Configuration | Environment variables, `.env` |
| Version control | Git, GitHub |
| Planned AI layer | LLM, RAG, Text-to-SQL |
| Planned interface | Streamlit |

## Project Structure

```text
AI-Powered-Food-Delivery-Analytics-Platform/
├── data/
│   └── raw/                              # Local source CSVs (Git-ignored)
├── scripts/
│   ├── inspect_data.py                   # Inspect source datasets
│   ├── upload_to_s3.py                   # Upload datasets to S3
│   ├── snowflake_connection_test.py      # Test Snowflake connectivity
│   ├── execute_sql.py                    # Execute SQL files through Python
│   └── check_snowflake_stage.py          # Validate expected staged CSV files
├── sql/
│   ├── create_raw_tables.sql             # Create RAW tables
│   └── load_raw_data.sql                 # Load files using COPY INTO
├── food_delivery_dbt/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   │   ├── _sources.yml
│   │   │   ├── staging.yml
│   │   │   ├── stg_food.sql
│   │   │   ├── stg_menu.sql
│   │   │   ├── stg_restaurant.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_reviews.sql
│   │   │   └── stg_users.sql
│   │   ├── intermediate/
│   │   │   ├── int_order_item_enriched.sql
│   │   │   └── intermediate.yml
│   │   └── marts/
│   │       ├── mart_food_popularity.sql
│   │       ├── mart_restaurant_performance.sql
│   │       ├── mart_menu_pricing.sql
│   │       ├── mart_review_analytics.sql
│   │       └── marts.yml
│   ├── analyses/
│   ├── macros/
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
├── airflow/
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── dags/
│   │   ├── food_delivery_pipeline.py
│   │   └── food_delivery_pipeline_smoke_test.py
│   └── dbt_profiles/
│       └── profiles.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Local environment files, raw datasets, generated logs, and generated Airflow configuration are excluded from version control.

## Source Datasets

The project uses six CSV datasets:

| Dataset | Description |
|---|---|
| `food.csv` | Food identifiers, item names, and vegetarian classification |
| `menu.csv` | Menu identifiers, restaurant and food references, cuisine, and prices |
| `restaurant.csv` | Restaurant names, cities, ratings, costs, cuisines, and additional details |
| `order_items.csv` | Order-item identifiers, order references, food and restaurant references, prices, quantities, and line amounts |
| `reviews.csv` | Review records, order and user references, ratings, comments, and dates |
| `users.csv` | User identifiers and demographic attributes |

**Dataset limitation:** The source data does not include an `orders.csv` file. Order-level activity is therefore derived from `order_items.csv`. Missing attributes such as delivery times and order statuses are not invented.

---

## Milestone 1 — AWS S3 Data Ingestion

**Status: Completed**

### Implementation

- Created an Amazon S3 bucket in the `ap-south-1` (Mumbai) region.
- Configured S3 Block Public Access.
- Enabled server-side encryption using SSE-S3.
- Uploaded all six CSV datasets to the `raw/` prefix.
- Implemented Python-based uploads using `boto3`.
- Configured local AWS authentication through the AWS CLI credential provider.

### S3 Configuration

| Setting | Value |
|---|---|
| Bucket | `ashwin-food-analytics-raw-80208` |
| Region | `ap-south-1` |
| Prefix | `raw/` |
| Access | Private |

### Outcome

The raw datasets are stored in S3 and available for controlled ingestion into Snowflake.

## Milestone 2 — Snowflake RAW Layer

**Status: Completed**

### Infrastructure

- Created the `FOOD_DELIVERY_DB` database.
- Created the `RAW` schema.
- Configured the `FOOD_S3_INTEGRATION` storage integration.
- Configured the associated AWS IAM role and access policy.
- Created the external stage `FOOD_DELIVERY_DB.RAW.FOOD_S3_STAGE`.
- Validated access to the S3 files from Snowflake.

### Implementation

- Developed a Python Snowflake connection test.
- Implemented `scripts/execute_sql.py` for executing SQL files.
- Created six RAW tables using `sql/create_raw_tables.sql`.
- Loaded CSV datasets using `COPY INTO` statements in `sql/load_raw_data.sql`.
- Used explicit column mappings to accommodate extra source index columns.
- Excluded direct identifiers and the source password column from the loaded `RAW_USERS` table.

### Ingestion Results

| RAW table | Rows |
|---|---:|
| `RAW_FOOD` | 371,561 |
| `RAW_MENU` | 1,179,936 |
| `RAW_ORDER_ITEMS` | 22,998,179 |
| `RAW_RESTAURANT` | 148,541 |
| `RAW_REVIEWS` | 300,000 |
| `RAW_USERS` | 100,000 |
| **Total** | **25,098,217** |

### Validation

- Verified the six RAW tables and their row counts.
- Checked selected key columns for NULL values.
- Confirmed that `NAME`, `EMAIL`, and `PASSWORD` were absent from `RAW_USERS`.
- Verified the uniqueness of loaded `ORDER_ITEM_ID` values.
- Reran the loading script and observed that Snowflake skipped previously loaded files in this scenario.
- Confirmed that row counts remained unchanged after the rerun.

The rerun demonstrates Snowflake's file load-history behavior for the tested scenario. Recovery from partial failures and broader idempotency testing remain opportunities for improvement.

## Milestone 3 — dbt Staging Transformations

**Status: Completed and verified**

### Objective

Create a maintainable SQL transformation layer between the Snowflake RAW tables and downstream analytical models.

### Implementation

- Installed dbt Core and the Snowflake adapter.
- Initialized the `food_delivery_dbt` project.
- Configured the dbt Snowflake profile.
- Defined explicit source references in `models/staging/_sources.yml`.
- Implemented six staging models.
- Used `TRIM()` and `NULLIF()` to clean text fields and normalize empty strings.
- Applied Snowflake conversion functions such as `TRY_TO_NUMBER`, `TRY_TO_DECIMAL`, and `TRY_TO_DATE` where appropriate.
- Materialized staging models as Snowflake views.
- Executed the models and verified their output using `dbt show`.

### Staging Models

| Model | Purpose |
|---|---|
| `stg_food` | Standardizes food identifiers, names, and food classifications |
| `stg_menu` | Cleans menu data and converts prices into numeric values |
| `stg_restaurant` | Standardizes restaurant identifiers, names, cities, ratings, costs, and details |
| `stg_order_items` | Cleans order-item references, prices, quantities, and line amounts |
| `stg_reviews` | Standardizes review identifiers, ratings, comments, and dates |
| `stg_users` | Cleans demographic attributes while retaining the privacy-safe RAW schema |

### Verification

- Confirmed the dbt project parsed successfully.
- Successfully built all six staging views.
- Previewed transformed output using `dbt show`.
- Verified that the staging models referenced the declared Snowflake sources.

The staging layer provides standardized columns and more appropriate data types for subsequent analytics.

## Milestone 4 — Intermediate Models and Analytics Marts

**Status: Completed and data-quality tests passed**

### Objective

Transform cleaned staging data into reusable, business-oriented analytical datasets.

### Intermediate Model

| Model | Purpose |
|---|---|
| `int_order_item_enriched` | Enriches order-item records with food names, food categories, and restaurant details |

The intermediate model uses dbt `ref()` dependencies and left joins to preserve unmatched order-item records.

### Join Validation

The row count of the source staging model and enriched intermediate model was verified:

| Model | Rows |
|---|---:|
| `stg_order_items` | 22,998,179 |
| `int_order_item_enriched` | 22,998,179 |

Additional checks returned no duplicate restaurant IDs or food IDs in the corresponding staging models for the tested queries.

This validated the observed row-count preservation for the current dataset. The checks should be retained as part of ongoing data-quality monitoring.

### Analytics Marts

| Model | Purpose |
|---|---|
| `mart_food_popularity` | Aggregates order-item counts, distinct order counts, quantities sold, recorded line amounts, and average unit prices by food |
| `mart_restaurant_performance` | Combines restaurant details with aggregated order-item metrics and review metrics |
| `mart_menu_pricing` | Provides menu-level prices and food-level minimum, maximum, and average prices across menu records |
| `mart_review_analytics` | Aggregates review counts, average review ratings, rating categories, and review date ranges |

### Important Metric Definitions

- `order_item_count` represents order-item records, not distinct orders.
- `distinct_order_count` counts distinct order IDs associated with the food or restaurant.
- `total_recorded_revenue` is calculated from the supplied `line_amount` field. It should be interpreted according to the source dataset's definition of that field.
- `mart_menu_pricing` remains at menu-record grain; `food_id` is not expected to be unique in this mart.
- The restaurant's listed rating is kept separate from the average rating calculated from its review records.

### Data-Quality Tests

Added dbt tests for:
- Non-null and unique identifiers in selected staging models.
- Unique order-item identifiers in the intermediate model.
- Relationships from enriched order items to food and restaurant staging models.
- Required identifiers and key constraints in the analytics marts.

The combined `dbt test` suite completed successfully for the defined tests.

### Verification

- Successfully executed the intermediate model and all four marts.
- Previewed model output in Snowflake.
- Queried the menu pricing mart to verify populated pricing metrics.
- Built the complete dbt project.
- Ran the combined data-quality test suite with all defined tests passing.

## Milestone 5 — Apache Airflow Orchestration

**Status: Implemented and locally verified**

### Objective

Orchestrate the existing Snowflake ingestion and dbt transformation workflow through Apache Airflow, providing task dependencies, retries, logs, and execution monitoring.

### Infrastructure

- Set up Apache Airflow using Docker Compose and Docker Desktop with WSL2 on Windows.
- Created a custom image based on Apache Airflow `3.3.2`.
- Installed dbt Core `1.12.6` and dbt-snowflake `1.12.4` in an isolated Python virtual environment inside the image.
- Added the required Python dependencies for S3 and Snowflake integration.
- Configured PostgreSQL as the Airflow metadata database and Redis with the CeleryExecutor.
- Configured the dbt profile to use environment variables for Snowflake credentials.
- Kept local secrets separate from the tracked project configuration.

### Pipeline DAG

The primary DAG is `food_delivery_data_pipeline`, which executes these tasks in dependency order:

```text
check_pipeline_environment
             |
             v
validate_snowflake_stage
             |
             v
load_snowflake_raw_tables
             |
             v
build_dbt_models_and_tests
```

**Task responsibilities:**

1. `check_pipeline_environment` — verifies required Snowflake environment variables are available without printing their values.
2. `validate_snowflake_stage` — checks that the six expected CSV files are available in the Snowflake external stage.
3. `load_snowflake_raw_tables` — executes the existing `sql/load_raw_data.sql` script through the Python SQL runner.
4. `build_dbt_models_and_tests` — executes `dbt build`, including model builds and configured tests.

The DAG is configured for manual execution with `schedule=None`. It includes retries and task dependency ordering.

A separate `food_delivery_pipeline_smoke_test` DAG was also created and successfully executed to verify task execution in the Airflow environment.

### Validation

- Confirmed that the Airflow services started and reached healthy status.
- Verified the custom dbt-enabled Docker image.
- Confirmed dbt and the Snowflake adapter were available inside the image.
- Ran `dbt debug` successfully against the configured Snowflake connection.
- Verified that all six expected CSV files were found in the Snowflake external stage.
- Successfully executed all four tasks in `food_delivery_data_pipeline`.
- Confirmed that the full DAG completed successfully.

### Execution

From the `airflow/` directory, start the local services:

```powershell
docker compose up -d
docker compose ps
```

Open the Airflow UI at `http://localhost:8080` and trigger `food_delivery_data_pipeline` manually.

This Docker Compose environment is intended for local development and demonstration, not for production deployment.

---

## Security and Data Management

- Keep `.env`, `airflow/pipeline.env`, and other credential files out of Git.
- Never commit AWS credentials, Snowflake passwords, API keys, or Fernet keys.
- Keep the S3 bucket private and restrict IAM access to the required resources and prefix.
- Do not commit the raw CSV datasets.
- The source `users.csv` contains personal information and a plaintext password-like column. Do not expose the raw file or load raw passwords into analytical tables.
- Use environment-variable references in dbt profiles rather than hardcoded credentials.
- Exclude generated Airflow logs and configuration and dbt-generated artifacts from version control.
- Use least-privilege AWS and Snowflake roles for application access. The initial development environment uses administrative privileges that should be reduced before production deployment.
- Do not use this local Docker Compose configuration as a public production deployment without additional hardening.

## Local Setup

### Prerequisites

- Python and pip
- AWS CLI
- An AWS account with access to the configured S3 bucket
- A Snowflake account with the required database and integration permissions
- Docker Desktop and Docker Compose
- Git

### 1. Clone the Repository

```powershell
git clone https://github.com/Ashwin-Vivegan/AI-Powered-Food-Delivery-Analytics-Platform.git
cd AI-Powered-Food-Delivery-Analytics-Platform
```

### 2. Set Up the Python Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

dbt dependencies are installed separately for local development:

```powershell
python -m pip install dbt-core dbt-snowflake
```

### 3. Configure Local Credentials

Create a local `.env` file based on `.env.example`, then supply the required Snowflake values.

For AWS operations, configure the AWS CLI credential provider. Never share or commit the contents of credential files.

### 4. Run Snowflake Ingestion Scripts

Create the RAW tables:

```powershell
python scripts/execute_sql.py sql/create_raw_tables.sql
```

Load the datasets:

```powershell
python scripts/execute_sql.py sql/load_raw_data.sql
```

These scripts depend on the previously configured Snowflake database, schema, integration, and external stage.

### 5. Run dbt Transformations

From the dbt project directory:

```powershell
cd food_delivery_dbt
dbt debug
dbt parse
dbt build
```

The dbt profile must reference the correct Snowflake account and credentials through locally configured environment variables.

### 6. Start Airflow

From the repository's `airflow/` directory:

```powershell
docker compose up -d
docker compose ps
```

The local Airflow environment uses the custom Docker image and mounted project resources. The `airflow/pipeline.env` and local dbt profile must be configured before executing the full DAG.

## Roadmap

### Completed

- [x] Milestone 1: AWS S3 setup and raw dataset upload
- [x] Milestone 2: Snowflake integration, external stage, RAW tables, loading, and initial validation
- [x] Milestone 3: dbt project and six staging models
- [x] Milestone 4: Intermediate model, four analytics marts, and passing configured dbt tests
- [x] Milestone 5: Apache Airflow setup and successful end-to-end local pipeline execution

### Planned

- [ ] **Milestone 6: AI-Powered Analytics** — Integrate an LLM with governed access to the analytics models; implement RAG and validated Text-to-SQL.
- [ ] **Milestone 7: Streamlit Application** — Build an interactive dashboard for food delivery analytics and natural-language queries.
- [ ] **Milestone 8: Productionization and Deployment** — Configure CI/CD, secure secret management, hosted orchestration, application deployment, monitoring, alerting, reliability checks, evaluation, and cost controls.

## Project Goal

The long-term goal is to create a complete food delivery analytics platform that combines cloud data engineering, SQL-based transformation, workflow orchestration, and AI-powered querying. The platform aims to make analytical insights more accessible while maintaining reliable data processing, clear metric definitions, and appropriate data security.
