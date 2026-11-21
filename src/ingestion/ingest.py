
from pathlib import Path
import logging

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "extracted"
    / "online_retail_II.xlsx"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "online_retail_raw.parquet"

logger = logging.getLogger(__name__)


def ingest_retail_data() -> pd.DataFrame:
    """Ingest, standardize and save both Online Retail II sheets."""

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {SOURCE_FILE}"
        )

    sheet_names = [
        "Year 2009-2010",
        "Year 2010-2011"
    ]

    dataframes = []

    for sheet_name in sheet_names:
        logger.info("Reading sheet: %s", sheet_name)

        df = pd.read_excel(
            SOURCE_FILE,
            sheet_name=sheet_name,
            engine="openpyxl"
        )

        df["Invoice"] = df["Invoice"].astype("string")
        df["StockCode"] = df["StockCode"].astype("string")

        df["Customer ID"] = pd.to_numeric(
            df["Customer ID"],
            errors="coerce"
        ).astype("Int64")

        for column in df.select_dtypes(include=["object"]).columns:
            df[column] = df[column].astype("string")

        # Spark-compatible timestamp precision
        df["InvoiceDate"] = pd.to_datetime(
            df["InvoiceDate"],
            errors="coerce"
        ).astype("datetime64[us]")

        df["SourceYear"] = sheet_name
        dataframes.append(df)

    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    # Enforce microsecond precision after concatenation
    combined_df["InvoiceDate"] = combined_df[
        "InvoiceDate"
    ].astype("datetime64[us]")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    combined_df.to_parquet(
        OUTPUT_FILE,
        engine="pyarrow",
        index=False
    )

    logger.info(
        "Ingestion completed. Total records: %s",
        len(combined_df)
    )

    logger.info("Saved raw dataset: %s", OUTPUT_FILE)

    return combined_df


