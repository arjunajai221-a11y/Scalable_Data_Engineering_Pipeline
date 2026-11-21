from pathlib import Path
import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "online_retail_transformed.parquet"

logger = logging.getLogger(__name__)


def validate_retail_data(df: DataFrame) -> dict:
    """Run data quality checks on transformed retail data."""

    required_columns = [
        "invoice", "stock_code", "invoice_date",
        "quantity", "unit_price"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Required columns missing: {missing_columns}")

    logger.info("Starting data quality validation...")

    checks = df.agg(
        F.count("*").alias("total_records"),
        F.sum(F.when(F.col("invoice").isNull(), 1).otherwise(0)).alias("missing_invoice"),
        F.sum(F.when(F.col("stock_code").isNull(), 1).otherwise(0)).alias("missing_stock_code"),
        F.sum(F.when(F.col("invoice_date").isNull(), 1).otherwise(0)).alias("missing_invoice_date"),
        F.sum(F.when(F.col("quantity").isNull(), 1).otherwise(0)).alias("missing_quantity"),
        F.sum(F.when(F.col("unit_price").isNull(), 1).otherwise(0)).alias("missing_unit_price"),
        F.sum(F.when(F.col("customer_id").isNull(), 1).otherwise(0)).alias("missing_customer_id"),
        F.sum(F.when(F.col("description").isNull(), 1).otherwise(0)).alias("missing_description"),
        F.sum(F.when(F.col("quantity") == 0, 1).otherwise(0)).alias("zero_quantity_records"),
        F.sum(F.when(F.col("unit_price") < 0, 1).otherwise(0)).alias("negative_price_records"),
        F.sum(F.when(F.col("quantity") < 0, 1).otherwise(0)).alias("negative_quantity_records")
    ).first().asDict()

    checks["duplicate_records"] = (
        checks["total_records"] - df.dropDuplicates().count()
    )

    critical_checks = [
        "missing_invoice",
        "missing_stock_code",
        "missing_invoice_date",
        "missing_quantity",
        "missing_unit_price"
    ]

    checks["validation_status"] = (
        "PASSED"
        if all(checks[column] == 0 for column in critical_checks)
        else "FAILED"
    )

    print("\n========== DATA QUALITY REPORT ==========")

    for key, value in checks.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("=========================================\n")

    logger.info("Data quality validation completed.")

    if checks["validation_status"] == "FAILED":
        raise ValueError("Data quality validation failed.")

    return checks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    spark = (
        SparkSession.builder
        .appName("RetailDataQualityValidation")
        .master("local[*]")
        .getOrCreate()
    )

    try:
        if not INPUT_FILE.exists():
            raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

        df = spark.read.parquet(str(INPUT_FILE))
        validate_retail_data(df)

    finally:
        spark.stop()
