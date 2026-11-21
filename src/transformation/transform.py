
from pathlib import Path
import logging

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StringType,
    IntegerType,
    DoubleType,
    TimestampType
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "online_retail_raw.parquet"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "online_retail_transformed.parquet"

logger = logging.getLogger(__name__)


def transform_retail_data(spark: SparkSession) -> DataFrame:
    """
    Read ingested Parquet data, standardize columns,
    calculate revenue, and save transformed data.
    """

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    logger.info("Reading raw Parquet dataset...")

    df = spark.read.parquet(str(INPUT_FILE))

    # Standardize column names
    df = df.withColumnRenamed("Invoice", "invoice")
    df = df.withColumnRenamed("StockCode", "stock_code")
    df = df.withColumnRenamed("Description", "description")
    df = df.withColumnRenamed("Quantity", "quantity")
    df = df.withColumnRenamed("InvoiceDate", "invoice_date")
    df = df.withColumnRenamed("Price", "unit_price")
    df = df.withColumnRenamed("Customer ID", "customer_id")
    df = df.withColumnRenamed("Country", "country")
    df = df.withColumnRenamed("SourceYear", "source_year")

    # Apply data types
    df = (
        df.withColumn("invoice", F.col("invoice").cast(StringType()))
        .withColumn("stock_code", F.col("stock_code").cast(StringType()))
        .withColumn("description", F.trim(F.col("description").cast(StringType())))
        .withColumn("quantity", F.col("quantity").cast(IntegerType()))
        .withColumn("invoice_date", F.to_timestamp("invoice_date"))
        .withColumn("unit_price", F.col("unit_price").cast(DoubleType()))
        .withColumn("customer_id", F.col("customer_id").cast(IntegerType()))
        .withColumn("country", F.trim(F.col("country").cast(StringType())))
    )

    # Calculate transaction revenue
    df = df.withColumn(
        "revenue",
        F.round(
            F.col("quantity") * F.col("unit_price"),
            2
        )
    )

    # Add date-based analytical columns
    df = (
        df.withColumn("invoice_year", F.year("invoice_date"))
        .withColumn("invoice_month", F.month("invoice_date"))
        .withColumn("invoice_day", F.dayofmonth("invoice_date"))
    )

    # Remove rows without essential transaction information
    df = df.filter(
        F.col("invoice").isNotNull()
        & F.col("stock_code").isNotNull()
        & F.col("invoice_date").isNotNull()
        & F.col("quantity").isNotNull()
        & F.col("unit_price").isNotNull()
    )

    # Preserve cancellations and negative transactions.
    # Do not remove negative quantity or price records.

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Writing transformed Parquet dataset...")

    df.write.mode("overwrite").parquet(str(OUTPUT_FILE))

    logger.info("Transformation completed successfully.")

    return df
