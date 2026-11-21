from datetime import datetime, timezone

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def ingest_task():
    from src.ingestion.ingest import ingest_retail_data
    ingest_retail_data()


def transform_task():
    from pyspark.sql import SparkSession
    from src.transformation.transform import transform_retail_data

    spark = (
        SparkSession.builder
        .appName("AirflowRetailTransformation")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

    try:
        transform_retail_data(spark)
    finally:
        spark.stop()


def validate_task():
    from pyspark.sql import SparkSession
    from src.validation.validate import (
        INPUT_FILE,
        validate_retail_data
    )

    spark = (
        SparkSession.builder
        .appName("AirflowRetailValidation")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

    try:
        df = spark.read.parquet(str(INPUT_FILE))
        validate_retail_data(df)
    finally:
        spark.stop()


def load_task():
    from src.database.load_data import main
    main()


with DAG(
    dag_id="retail_etl_pipeline",
    description="End-to-end Online Retail II data engineering pipeline",
    start_date=datetime(2026, 11, 20, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "data_engineering",
        "retries": 1,
    },
    tags=["retail", "etl", "pyspark", "mysql"],
) as dag:

    ingestion = PythonOperator(
        task_id="ingest_retail_data",
        python_callable=ingest_task,
    )

    transformation = PythonOperator(
        task_id="transform_retail_data",
        python_callable=transform_task,
    )

    validation = PythonOperator(
        task_id="validate_retail_data",
        python_callable=validate_task,
    )

    warehouse_load = PythonOperator(
        task_id="load_mysql_warehouse",
        python_callable=load_task,
    )

    ingestion >> transformation >> validation >> warehouse_load
