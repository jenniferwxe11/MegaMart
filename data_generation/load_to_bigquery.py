import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "mega-mart-storage"
DATASET = "raw"


def main():
    client = bigquery.Client(project=PROJECT_ID)

    # Create dataset (run once ideally)
    dataset_id = f"{PROJECT_ID}.{DATASET}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "asia-southeast1"
    client.create_dataset(dataset, exists_ok=True)

    print("=" * 60)
    print("Datasets ready to be loaded into BigQuery")
    print("=" * 60)

    print("\nLOADING TABLES:")

    def load_csv(table_name, file_path):
        df = pd.read_csv(file_path)

        table_id = f"{PROJECT_ID}.{DATASET}.{table_name}"

        job = client.load_table_from_dataframe(
            df,
            table_id,
            job_config=bigquery.LoadJobConfig(
                autodetect=True, write_disposition="WRITE_TRUNCATE"
            ),
        )

        job.result()

        print(f"  ✓ {table_name}  ({len(df)} rows)")

    if __name__ == "__main__":
        load_csv("customers", "data_generation/raw_data/customers_raw.csv")
        load_csv("stores", "data_generation/raw_data/stores_raw.csv")
        load_csv("products", "data_generation/raw_data/products_raw.csv")
        load_csv(
            "competitor_products",
            "data_generation/raw_data/competitor_products_raw.csv",
        )
        load_csv(
            "competitor_price_history",
            "data_generation/raw_data/competitor_price_history_raw.csv",
        )
        load_csv(
            "store_catalogues", "data_generation/raw_data/store_catalogues_raw.csv"
        )
        load_csv(
            "product_lifecycles", "data_generation/raw_data/product_lifecycles_raw.csv"
        )
        load_csv(
            "product_content_quality",
            "data_generation/raw_data/product_content_quality_raw.csv",
        )
        load_csv("stockout_events", "data_generation/raw_data/stockout_events_raw.csv")
        load_csv("stock_snapshots", "data_generation/raw_data/stock_snapshots_raw.csv")
        load_csv(
            "inventory_change_events",
            "data_generation/raw_data/inventory_change_events_raw.csv",
        )
        load_csv("campaigns", "data_generation/raw_data/campaigns_raw.csv")
        load_csv(
            "campaign_assignments",
            "data_generation/raw_data/campaign_assignments_raw.csv",
        )
        load_csv(
            "campaign_exposures", "data_generation/raw_data/campaign_exposures_raw.csv"
        )
        load_csv("bundle_items", "data_generation/raw_data/bundle_items_raw.csv")
        load_csv("bundle_pricings", "data_generation/raw_data/bundle_pricings_raw.csv")
        load_csv("bundles", "data_generation/raw_data/bundles_raw.csv")
        load_csv("promotions", "data_generation/raw_data/promotions_raw.csv")
        load_csv("clickstreams", "data_generation/raw_data/clickstreams_raw.csv")
        load_csv(
            "transaction_items", "data_generation/raw_data/transaction_items_raw.csv"
        )
        load_csv("transactions", "data_generation/raw_data/transactions_raw.csv")
        load_csv("product_reviews", "data_generation/raw_data/product_reviews_raw.csv")

        print("\n")
        print("=" * 60)
        print("✓ All Tables Loaded Successfully")
        print("=" * 60)


if __name__ == "__main__":
    main()
