# Scalable Data Engineering Pipeline

An end-to-end data engineering project that builds an automated ETL pipeline using Python, PySpark, MySQL, Apache Airflow, and Docker. The pipeline processes the UCI Online Retail II dataset, performs data transformation and quality validation, and loads the processed records into a MySQL data warehouse for analytical queries.

## Project Architecture

```text
UCI Online Retail II Dataset (Excel)
              |
              v
       Data Ingestion
          (Python)
              |
              v
    Raw Data (Parquet)
              |
              v
   Data Transformation
          (PySpark)
              |
              v
   Data Quality Validation
              |
              v
      MySQL Data Warehouse
              |
              v
       SQL Analytics
              |
              v
   Apache Airflow Orchestration
              |
              v
          Docker
```

## Technologies Used

- Python
- Pandas
- PySpark
- MySQL
- SQL
- Apache Airflow
- Docker & Docker Compose
- Parquet
- Git & GitHub

## Dataset

**UCI Online Retail II Dataset**

- Two Excel worksheets covering 2009–2010 and 2010–2011.
- Combined dataset: 1,067,371 records.
- Transaction-level retail data containing invoices, products, quantities, prices, dates, customers, and countries.

## ETL Pipeline

### 1. Data Ingestion
- Reads both Excel worksheets.
- Combines the datasets.
- Standardizes data types.
- Stores raw data in Parquet format.

### 2. Data Transformation
- Uses PySpark for distributed data processing.
- Renames and standardizes columns.
- Converts data types.
- Calculates transaction revenue.
- Extracts date-related analytical fields.
- Stores transformed data in Parquet format.

### 3. Data Quality Validation
- Checks required columns.
- Identifies missing values.
- Checks zero quantities and negative prices.
- Identifies negative quantities and duplicate records.
- Retains return and cancellation records for analysis.

### 4. Data Warehouse Loading
- Loads transformed records into MySQL.
- Uses batch-based data insertion.
- Stores records in the `fact_retail_transactions` table.

### 5. Workflow Orchestration
Apache Airflow manages the complete ETL workflow through four sequential tasks:

1. `ingest_retail_data`
2. `transform_retail_data`
3. `validate_retail_data`
4. `load_mysql_warehouse`

The workflow is containerized and executed using Docker Compose.

## Data Validation Results

| Metric | Result |
|---|---:|
| Total records | 1,067,371 |
| Missing invoice numbers | 0 |
| Missing stock codes | 0 |
| Missing transaction dates | 0 |
| Missing quantities | 0 |
| Missing unit prices | 0 |
| Missing customer IDs | 243,007 |
| Missing descriptions | 4,382 |
| Negative quantities | 22,950 |
| Negative prices | 5 |
| Duplicate records | 12,133