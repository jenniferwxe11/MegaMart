# data_ingestion/load_to_bigquery.py

import logging
import subprocess

import pandas as pd
from google.cloud import bigquery

from data_ingestion.config.bigquery_config import (
    BIGQUERY_DATASET,
    BIGQUERY_LOCATION,
    PROJECT_ID,
    TABLES,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def ensure_correct_dtypes(df, schema):
    for field in schema:
        col_name = field.name
        col_type = field.field_type

        if col_type == "STRING":
            df[col_name] = df[col_name].astype("string")
        elif col_type == "INTEGER":
            df[col_name] = pd.to_numeric(df[col_name], errors="coerce").astype("Int64")
        elif col_type == "FLOAT":
            df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
        elif col_type == "BOOL":
            df[col_name] = (
                df[col_name]
                .astype("string")
                .str.strip()
                .str.lower()
                .map(
                    {
                        "true": True,
                        "false": False,
                    }
                )
                .astype("boolean")
            )
        elif col_type == "TIMESTAMP":
            df[col_name] = pd.to_datetime(df[col_name], errors="coerce", utc=True)
        elif col_type == "DATE":
            df[col_name] = pd.to_datetime(df[col_name], errors="coerce").dt.date


def load_csv(client, dataset_name, table_name, df, schema):
    table_id = f"{PROJECT_ID}.{dataset_name}.{table_name}"

    logger.info("Loading %s", table_name)
    logger.info(df.dtypes)

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(
            schema=schema,
            write_disposition="WRITE_TRUNCATE",
        ),
    )

    try:
        job.result()
    except Exception as e:
        logger.error(
            "Failed to load %s (%d rows): %s",
            table_name,
            len(df),
            str(e),
        )
        raise

    logger.info(
        "Loaded %s (%d rows)",
        table_name,
        len(df),
    )


def validate_schema(df, schema, table_name):
    expected_columns = {field.name for field in schema}
    actual_columns = set(df.columns)

    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns

    if missing_columns:
        raise ValueError(
            f"Table '{table_name}' is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if extra_columns:
        raise ValueError(
            f"Table '{table_name}' contains unexpected columns: "
            f"{sorted(extra_columns)}"
        )


def upload_tables(client, dataset_name):

    for table_name, config in TABLES.items():
        path = config["csv"]

        if not path.exists():
            raise FileNotFoundError(f"CSV file for {table_name} not found at {path}")

        df = pd.read_csv(path)

        validate_schema(df, config["schema"], table_name)

        ensure_correct_dtypes(df, config["schema"])

        if df.empty:
            logger.warning(
                "Skipping %s (empty CSV)",
                table_name,
            )
            continue

        load_csv(client, dataset_name, table_name, df, config["schema"])


def run_ingestion(dataset_name: str):
    client = bigquery.Client(project=PROJECT_ID)

    # Create dataset (run once ideally)
    dataset_id = f"{PROJECT_ID}.{dataset_name}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = BIGQUERY_LOCATION
    client.create_dataset(dataset, exists_ok=True)

    logger.info("=" * 60)
    logger.info("Datasets ready to be loaded into BigQuery")
    logger.info("=" * 60)

    logger.info("\nLOADING TABLES:")

    upload_tables(client, dataset_name)

    subprocess.run(
        [
            "dbt",
            "seed",
            "--project-dir",
            "dbt",
            "--profiles-dir",
            "dbt_profiles",
        ],
        check=True,
    )

    logger.info("\n")
    logger.info("=" * 60)
    logger.info("✓ All Tables Loaded Successfully")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_ingestion(BIGQUERY_DATASET)
