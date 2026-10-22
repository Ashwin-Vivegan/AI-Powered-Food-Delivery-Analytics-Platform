# AI Food Delivery Analytics

An end-to-end data engineering and AI analytics platform for food delivery data. The project establishes a cloud-based data pipeline using AWS S3 and Snowflake, with planned extensions for transformation, orchestration, and AI-powered analytics.

## Architecture

**Current implementation:**

AWS S3 → Snowflake Storage Integration → External Stage → Python SQL Executor → RAW Tables

**Planned architecture:**

S3 → Snowflake → dbt → Airflow → LLM → RAG / Text-to-SQL → Streamlit

## Tech Stack

- **Cloud Storage:** Amazon S3
- **Data Warehouse:** Snowflake
- **Programming Language:** Python
- **Data Ingestion:** Snowflake `COPY INTO`
- **Configuration:** Environment variables using `.env`
- **Planned:** dbt, Apache Airflow, LLM, RAG, Text-to-SQL, Streamlit

## Project Structure

```text
.
├── data/
│   └── raw/                         # Local source datasets (excluded from Git)
├── scripts/
│   ├── inspect_data.py              # Inspect source CSV datasets
│   ├── upload_to_s3.py              # Upload CSV datasets to S3
│   ├── snowflake_connection_test.py # Test Snowflake connectivity
│   └── execute_sql.py               # Execute SQL files through Python
├── sql/
│   ├── create_raw_tables.sql        # Create Snowflake RAW tables
│   └── load_raw_data.sql             # Load CSVs using COPY INTO
├── .env.example                     # Example environment configuration
├── .gitignore
├── requirements.txt
└── README.md
```

## Milestone 1: AWS S3 Ingestion

- Created an Amazon S3 bucket in the `ap-south-1` (Mumbai) region.
- Configured S3 Block Public Access.
- Enabled server-side encryption using SSE-S3.
- Uploaded six CSV datasets to the `raw/` prefix.
- Implemented a Python upload script using `boto3`.

### Source Datasets

| Dataset | Description |
|---|---|
| `food.csv` | Food item information |
| `menu.csv` | Restaurant menu and pricing data |
| `order_items.csv` | Individual order line items |
| `restaurant.csv` | Restaurant information |
| `reviews.csv` | Customer review records |
| `users.csv` | User demographic and account-related data |

## Milestone 2: Snowflake RAW Layer

### Infrastructure

- Created the Snowflake database `FOOD_DELIVERY_DB`.
- Created the `RAW` schema.
- Configured the `FOOD_S3_INTEGRATION` storage integration.
- Created the `FOOD_S3_STAGE` external stage pointing to the S3 `raw/` prefix.
- Validated the storage integration and confirmed Snowflake could list files from S3.

### Implementation

- Added a Python script to execute SQL files against Snowflake.
- Created six RAW tables using `sql/create_raw_tables.sql`.
- Loaded the CSV datasets using `COPY INTO` statements in `sql/load_raw_data.sql`.
- Used explicit column mappings to handle the extra index columns in source CSVs.
- Excluded direct identifiers and the plaintext password column from the `RAW_USERS` table.

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

- Verified that all six RAW tables were created.
- Confirmed the expected row counts after ingestion.
- Checked selected key columns for NULL values; all tested counts were zero.
- Verified that `NAME`, `EMAIL`, and `PASSWORD` were absent from `RAW_USERS`.
- Confirmed that `ORDER_ITEM_ID` values were unique in the loaded order-items table.
- Reran the ingestion script and observed that Snowflake processed zero new files for the previously loaded datasets.
- Rechecked row counts and confirmed they remained unchanged.

The rerun test demonstrates that Snowflake skipped previously loaded files in this scenario. Recovery from partial failures and more comprehensive idempotency testing remain future improvements.

## Security Considerations

- Keep `.env` out of version control.
- Do not commit AWS credentials, Snowflake passwords, or API keys.
- Keep the S3 bucket private and restrict IAM permissions to the required prefix.
- The source `users.csv` contains personal information and a plaintext password column. Do not expose the source file or load raw passwords into analytical tables.
- Use least-privilege roles for application access rather than relying on administrative credentials for routine operations.

## Setup

### 1. Create and activate the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file based on `.env.example`. Supply the required Snowflake connection settings locally. AWS SDK operations can use the AWS CLI credential provider when configured.

### 4. Execute SQL scripts

Create the RAW tables:

```powershell
python scripts/execute_sql.py sql/create_raw_tables.sql
```

Load the source datasets:

```powershell
python scripts/execute_sql.py sql/load_raw_data.sql
```

The SQL scripts use the existing Snowflake external stage. AWS and Snowflake infrastructure must be configured before running these commands.

## Roadmap

- [x] Milestone 1: AWS S3 setup and dataset upload
- [x] Milestone 2 infrastructure: Snowflake integration and external stage
- [x] Milestone 2 ingestion: RAW tables, CSV loading, and initial validation
- [ ] Milestone 3: Data transformation using dbt
- [ ] Milestone 4: Pipeline orchestration using Apache Airflow
- [ ] Milestone 5: LLM-based data enrichment
- [ ] Milestone 6: Retrieval-Augmented Generation (RAG)
- [ ] Milestone 7: Text-to-SQL analytics
- [ ] Milestone 8: Streamlit dashboard, evaluation, and deployment
