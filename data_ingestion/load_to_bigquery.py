import logging
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

from data_ingestion.config.bigquery_config import (
    PROJECT_ID,
    RAW_DATASET,
    TABLES,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_csv(client, table_name, df):
    table_id = f"{PROJECT_ID}.{RAW_DATASET}.{table_name}"
    schema = TABLES[table_name]["schema"]

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


def upload_tables(client):

    for table_name, config in TABLES.items():
        path = Path(config["csv"])

        if not path.exists():
            raise FileNotFoundError(f"CSV file for {table_name} not found at {path}")

        df = pd.read_csv(path)

        if df.empty:
            logger.warning(
                "Skipping %s (empty CSV)",
                table_name,
            )
            continue

        load_csv(client, table_name, df)


def main():
    client = bigquery.Client(project=PROJECT_ID)

    # Create dataset (run once ideally)
    dataset_id = f"{PROJECT_ID}.{RAW_DATASET}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "asia-southeast1"
    client.create_dataset(dataset, exists_ok=True)

    logger.info("=" * 60)
    logger.info("Datasets ready to be loaded into BigQuery")
    logger.info("=" * 60)

    logger.info("\nLOADING TABLES:")

    upload_tables(client)

    logger.info("\n")
    logger.info("=" * 60)
    logger.info("✓ All Tables Loaded Successfully")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
