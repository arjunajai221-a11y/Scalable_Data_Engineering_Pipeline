from pathlib import Path
import logging
import pyarrow.dataset as ds
from src.database.mysql_connection import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "online_retail_transformed.parquet"
TABLE_NAME = "fact_retail_transactions"
BATCH_SIZE = 5000

COLUMNS = [
    "invoice", "stock_code", "description", "quantity",
    "invoice_date", "unit_price", "customer_id", "country",
    "source_year", "revenue", "invoice_year",
    "invoice_month", "invoice_day"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_table(connection):
    cursor = connection.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            invoice VARCHAR(20),
            stock_code VARCHAR(30),
            description TEXT,
            quantity INT,
            invoice_date DATETIME,
            unit_price DECIMAL(12,4),
            customer_id INT NULL,
            country VARCHAR(100),
            source_year VARCHAR(20),
            revenue DECIMAL(14,2),
            invoice_year SMALLINT,
            invoice_month TINYINT,
            invoice_day TINYINT,
            INDEX idx_invoice (invoice),
            INDEX idx_customer_id (customer_id),
            INDEX idx_invoice_date (invoice_date),
            INDEX idx_country (country)
        )
    """)
    connection.commit()
    cursor.close()
    logger.info("Warehouse table is ready.")


def load_data(connection):
    dataset = ds.dataset(str(INPUT_FILE), format="parquet")
    scanner = dataset.scanner(columns=COLUMNS, batch_size=BATCH_SIZE)

    cursor = connection.cursor()
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    column_names = ", ".join(f"`{column}`" for column in COLUMNS)

    insert_query = f"""
        INSERT INTO {TABLE_NAME} ({column_names})
        VALUES ({placeholders})
    """

    cursor.execute(f"TRUNCATE TABLE {TABLE_NAME}")
    connection.commit()

    total_loaded = 0

    for record_batch in scanner.to_batches():
        rows = [
            tuple(row[column] for column in COLUMNS)
            for row in record_batch.to_pylist()
        ]

        cursor.executemany(insert_query, rows)
        connection.commit()

        total_loaded += len(rows)
        logger.info("Records loaded: %s", total_loaded)

    cursor.close()
    return total_loaded


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

    connection = None

    try:
        logger.info("Reading transformed Parquet dataset...")
        connection = get_connection()

        create_table(connection)
        total_loaded = load_data(connection)

        print("\n========== DATA WAREHOUSE LOAD REPORT ==========")
        print("Target table:", TABLE_NAME)
        print("Records loaded:", total_loaded)
        print("Batch size:", BATCH_SIZE)
        print("Load status: SUCCESS")
        print("================================================\n")

    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        raise

    finally:
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
