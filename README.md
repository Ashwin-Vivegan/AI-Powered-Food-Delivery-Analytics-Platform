# AI-Powered Food Delivery Analytics Platform

An end-to-end data engineering and AI analytics platform that transforms raw food delivery data into analytics-ready datasets and enables users to explore business insights through natural-language questions.

Built using **AWS S3, Snowflake, dbt, Apache Airflow, FastAPI, RAG, Groq, SQLGlot, Streamlit and Docker**.

## Project Overview

Food delivery platforms generate large volumes of data about restaurants, menus, food items, orders, users and customer reviews. Extracting meaningful insights from this data requires reliable ingestion, transformation, orchestration and analytics.

This project implements a complete data engineering pipeline alongside an AI-powered analytics interface.

The platform allows users to:
- Ingest raw food delivery datasets into AWS S3.
- Load and transform data in Snowflake using dbt.
- Orchestrate ingestion and transformation workflows using Apache Airflow.
- Ask analytical questions in natural language.
- Retrieve metric definitions and analytical documentation using RAG.
- Generate and validate SQL using an LLM.
- Execute approved read-only queries against Snowflake.
- View answers, generated SQL and query results through Streamlit.

## Architecture

### Data Engineering Pipeline

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
        +--> Intermediate Models
        |
        +--> Analytics Marts
        |
        v
   Data Quality Tests
```

Apache Airflow orchestrates the Snowflake ingestion and dbt transformation workflow.

### AI Analytics Architecture

```text
       User Question
              |
              v
       Streamlit UI
              |
              v
          FastAPI
              |
       +------+------+
       |             |
       v             v
      RAG       Text-to-SQL
       |             |
       v             v
 Local Knowledge   Groq LLM
     Base              |
       |               v
       v          SQLGlot Validation
   Groq LLM             |
       |                v
       v          Read-only Snowflake
   AI Answer            |
                        v
                  Query Results
                        |
                        v
                   Streamlit UI
```

RAG retrieves relevant analytics documentation and metric definitions. Text-to-SQL generates queries using the available analytical models, validates them and executes approved read-only SQL against Snowflake.

### Overall Architecture

```text
AWS S3
   |
   v
Snowflake RAW Layer
   |
   v
dbt Transformations
   |
   v
Analytics Marts
   |
   +--------------------+
   |                    |
   v                    v
Apache Airflow       FastAPI AI
Orchestration        Analytics
                        |
                +-------+-------+
                |               |
                v               v
               RAG          Text-to-SQL
                                |
                                v
                           Snowflake
                                |
                                v
                            Streamlit
```

Airflow manages the data pipeline independently of the interactive analytics application.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python, SQL |
| Cloud Storage | Amazon S3 |
| Data Warehouse | Snowflake |
| Data Ingestion | Python, boto3, Snowflake COPY INTO |
| Data Transformation | dbt Core, dbt-snowflake |
| Workflow Orchestration | Apache Airflow |
| AI / LLM | Groq |
| Retrieval-Augmented Generation | Sentence Transformers, FAISS-style vector similarity retrieval |
| Embedding Model | all-MiniLM-L6-v2 |
| Text-to-SQL Validation | SQLGlot |
| Backend | FastAPI |
| Frontend | Streamlit |
| Containerization | Docker, Docker Compose |
| Testing | pytest, dbt tests |
| Version Control | Git, GitHub |
| Development Environment | Windows, WSL2 |

## Project Structure

```text
AI-Powered-Food-Delivery-Analytics-Platform/
|
├── ai_service/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── planner.py
│   │   ├── sql_generator.py
│   │   ├── snowflake_executor.py
│   │   ├── retriever.py
│   │   └── knowledge_answer.py
│   ├── knowledge/
│   │   └── analytics_catalog.md
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
|
├── streamlit_app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
|
├── airflow/
│   ├── dags/
│   ├── dbt_profiles/
│   ├── Dockerfile
│   └── docker-compose.yaml
|
├── food_delivery_dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── dbt_project.yml
│   └── tests/
|
├── scripts/
├── sql/
├── data/
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── requirements.txt
└── README.md
```

Local datasets, environment files, generated artifacts and credentials are excluded from version control.

## Source Datasets

The project uses six CSV datasets:

| Dataset | Description |
|---|---|
| food.csv | Food identifiers, names and classifications |
| menu.csv | Menu records, restaurant references, food references and prices |
| restaurant.csv | Restaurant details, cities, ratings and costs |
| order_items.csv | Order-item references, quantities, prices and line amounts |
| reviews.csv | Review records, ratings, comments and dates |
| users.csv | User identifiers and demographic attributes |

**Dataset limitation:** The source data does not include an `orders.csv` file. Order-level activity is derived from `order_items.csv`. Delivery times and order statuses are not available and are not fabricated.

---

## Milestone 1 — AWS S3 Data Ingestion

**Status: Completed**

- Created a private S3 bucket in the Mumbai region (`ap-south-1`).
- Enabled S3 Block Public Access.
- Configured SSE-S3 encryption.
- Uploaded all six CSV datasets using Python and boto3.
- Configured local AWS authentication through AWS CLI.

### S3 Configuration

| Setting | Value |
|---|---|
| Bucket | `ashwin-food-analytics-raw-80208` |
| Region | `ap-south-1` |
| Prefix | `raw/` |
| Access | Private |

## Milestone 2 — Snowflake RAW Layer

**Status: Completed**

- Created `FOOD_DELIVERY_DB` and the `RAW` schema.
- Configured the AWS storage integration and external stage.
- Created six RAW tables.
- Loaded CSV datasets using Snowflake `COPY INTO`.
- Used explicit column mappings.
- Excluded direct identifiers and the source password column from `RAW_USERS`.

### Ingestion Results

| RAW Table | Rows |
|---|---:|
| RAW_FOOD | 371,561 |
| RAW_MENU | 1,179,936 |
| RAW_ORDER_ITEMS | 22,998,179 |
| RAW_RESTAURANT | 148,541 |
| RAW_REVIEWS | 300,000 |
| RAW_USERS | 100,000 |
| **Total** | **25,098,217** |

Validated table counts, selected NULL checks, identifier uniqueness and repeated-load behavior.

## Milestone 3 — dbt Staging Transformations

**Status: Completed**

Implemented six staging models:

- `stg_food`
- `stg_menu`
- `stg_restaurant`
- `stg_order_items`
- `stg_reviews`
- `stg_users`

Implemented:
- Text cleaning and normalization.
- Explicit data-type conversions.
- NULL handling.
- Source declarations.
- Snowflake view materialization.

Successfully parsed and built all six staging models.

## Milestone 4 — Intermediate Models and Analytics Marts

**Status: Completed**

### Intermediate Model

`int_order_item_enriched`

Enriches order-item records with food names, categories and restaurant details.

Verified that the staging and enriched models both contain 22,998,179 rows.

### Analytics Marts

| Model | Purpose |
|---|---|
| `mart_food_popularity` | Food popularity, order-item counts, quantities and recorded revenue |
| `mart_restaurant_performance` | Restaurant-level order-item and review metrics |
| `mart_menu_pricing` | Menu-level pricing and food-level price statistics |
| `mart_review_analytics` | Review counts, average ratings and review date ranges |

### Important Metric Definitions

- `order_item_count` counts order-item records, not distinct orders.
- `distinct_order_count` counts distinct order IDs.
- `total_recorded_revenue` is the sum of recorded `line_amount` values. It is not independently verified accounting revenue, profit or net sales.
- `mart_menu_pricing` is maintained at menu-record grain.
- Restaurant-listed ratings are kept separate from review-derived average ratings.

### Data Quality

Added dbt tests for:
- Non-null and unique identifiers.
- Order-item uniqueness.
- Relationships between enriched records and source models.
- Required identifiers and mart constraints.

All configured dbt tests passed.

## Milestone 5 — Apache Airflow Orchestration

**Status: Implemented and locally verified**

Configured Apache Airflow 3.3.2 using Docker Compose.

Implemented:
- Custom Airflow Docker image.
- PostgreSQL metadata database.
- Redis and CeleryExecutor.
- Isolated dbt environment.
- Environment-based Snowflake configuration.
- Manual DAG execution and task retries.

### Pipeline DAG

`food_delivery_data_pipeline`

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

All four tasks were successfully executed.

A separate smoke-test DAG was also implemented and executed.

## Milestone 6 — AI-Powered Analytics

**Status: Implemented and locally verified**

Developed a FastAPI backend integrating Groq, local RAG retrieval and Snowflake analytics.

### RAG Implementation

- Uses `sentence-transformers/all-MiniLM-L6-v2`.
- Generates local 384-dimensional embeddings.
- Retrieves relevant analytics documentation using cosine similarity.
- Uses an analytics knowledge base containing mart definitions, metric definitions and data limitations.
- Supplies retrieved context to the LLM for grounded answers.

### Text-to-SQL

Implemented a natural-language analytics workflow:

1. Accepts a user's analytical question.
2. Retrieves relevant schema and metric documentation.
3. Uses Groq to generate a structured analytics plan.
4. Generates SQL for supported questions.
5. Validates SQL using SQLGlot and application-level rules.
6. Executes approved read-only SQL against Snowflake.
7. Returns results and generated SQL.

### Security Controls

- Dedicated `AI_ANALYTICS_READONLY` Snowflake role.
- Approved analytics marts and column allowlists.
- SELECT-only query validation.
- Restrictions on joins, subqueries, CTEs and `SELECT *`.
- Maximum 100 returned rows.
- Query timeout configuration.

### FastAPI Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | API information |
| `GET /health` | Health check |
| `POST /api/v1/analytics/plan` | Generate an analytics plan |
| `POST /api/v1/analytics/sql` | Generate and validate SQL |
| `POST /api/v1/analytics/query` | Generate, validate and execute an analytics query |
| `POST /api/v1/analytics/ask` | RAG-based knowledge question answering |

### Testing

Verified:
- Metric-definition questions through RAG.
- Supported natural-language analytics queries.
- SQL generation and execution.
- Unsupported questions being rejected when the required data is unavailable.

## Milestone 7 — Streamlit Analytics Application

**Status: Implemented and locally verified**

Developed a Streamlit interface connected to FastAPI.

### Features

- Backend URL configuration.
- API health checking.
- RAG-based Ask AI interface.
- Natural-language analytics query interface.
- Generated SQL display.
- Analytics plan display.
- Query result tables using Pandas.
- Error handling and unsupported-question feedback.

### Verified Scenarios

| Scenario | Result |
|---|---|
| Ask how total recorded revenue is calculated | Passed |
| Find the top 10 food items by recorded revenue | Passed |
| Ask about unavailable delivery-time metrics | Correctly rejected |
| Calculate average review ratings by city | Passed |

## Milestone 8 — Docker Containerization and Integration

**Status: Implemented and locally verified**

Containerized the FastAPI backend and Streamlit frontend.

### Docker Components

- `ai_service/Dockerfile`
- `streamlit_app/Dockerfile`
- Root `compose.yaml`
- Root `.dockerignore`

### Implementation

- Used Python slim images.
- Configured non-root application users.
- Installed CPU-only PyTorch for the local embedding model.
- Configured persistent Hugging Face model caching through a Docker volume.
- Connected FastAPI and Streamlit through Docker Compose networking.
- Configured API health checks.
- Configured Streamlit to start after the API becomes healthy.

### Run the Application

From the project root:

```powershell
docker compose up -d --build
```

Check service status:

```powershell
docker compose ps
```

View logs:

```powershell
docker compose logs -f
```

Access the applications:

- Streamlit: `http://localhost:8501`
- FastAPI: `http://localhost:8000`
- FastAPI Swagger: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

Stop the application:

```powershell
docker compose down
```

The Dockerized application was tested with RAG, Text-to-SQL and unsupported analytics questions. Restart and persistence checks were also completed.

**Note:** Airflow runs through its separate Docker Compose configuration under `airflow/`. It is not started by the root API/Streamlit Compose configuration.

---

## Security and Data Management

- Keep `.env` and other credential files out of Git.
- Never commit AWS credentials, Snowflake passwords, Groq API keys or Fernet keys.
- Keep S3 private and restrict IAM permissions.
- Do not commit raw CSV datasets.
- Do not expose the source user dataset or its password-like field.
- Use environment variables for Snowflake and application configuration.
- Use the read-only Snowflake role for AI analytics queries.
- Keep generated logs, caches and build artifacts out of version control.
- Review permissions and harden configurations before public production deployment.

The local Docker Compose setup is intended for development and demonstration, not as a production deployment configuration.

## Local Development Setup

### Prerequisites

- Python 3.13
- AWS CLI
- AWS account and configured S3 access
- Snowflake account and configured database, stage and permissions
- Docker Desktop and Docker Compose
- Git
- Groq API key

### 1. Clone the Repository

```powershell
git clone https://github.com/Ashwin-Vivegan/AI-Powered-Food-Delivery-Analytics-Platform.git

cd AI-Powered-Food-Delivery-Analytics-Platform
```

### 2. Configure Environment Variables

Create a local `.env` file using `.env.example` as the reference.

Configure the required Snowflake connection details, Groq API key and other variables expected by the application.

Never commit or share the actual `.env` file.

### 3. Start FastAPI and Streamlit with Docker

```powershell
docker compose up -d --build
```

Verify:

```powershell
docker compose ps
```

Open Streamlit at `http://localhost:8501`.

### 4. Run Airflow Separately

Configure the local Airflow environment files and dbt profile according to the provided examples and existing Airflow configuration.

From the `airflow/` directory:

```powershell
docker compose up -d
docker compose ps
```

Open the Airflow UI at `http://localhost:8080`.

Trigger `food_delivery_data_pipeline` manually.

### 5. Run dbt Locally (Optional)

Install dbt and the Snowflake adapter in your local Python environment, configure the dbt profile and run:

```powershell
cd food_delivery_dbt

dbt debug
dbt parse
dbt build
```

## Current Project Status

### Completed

- [x] Milestone 1: AWS S3 data ingestion
- [x] Milestone 2: Snowflake RAW layer
- [x] Milestone 3: dbt staging transformations
- [x] Milestone 4: Intermediate models and analytics marts
- [x] Milestone 5: Apache Airflow orchestration
- [x] Milestone 6: RAG and Text-to-SQL analytics backend
- [x] Milestone 7: Streamlit analytics interface
- [x] Milestone 8: Docker containerization and local integration

### Remaining Work

- [ ] Final clean-environment verification
- [ ] Complete deployment of the API and Streamlit application
- [ ] Production-ready secret management and configuration
- [ ] Monitoring, logging and alerting
- [ ] LLM evaluation and regression testing
- [ ] Final deployment and operational documentation

## Project Goal

The goal is to combine modern data engineering with AI-powered analytics to make business insights more accessible.

By integrating reliable cloud ingestion, warehouse transformations, workflow orchestration, retrieval-augmented generation and validated natural-language SQL, the platform demonstrates an end-to-end approach to building an AI-enabled analytics system.
