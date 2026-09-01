# data_ingestion/config/bigquery_config.py

"""
BigQuery configuration.

Environment variables:

BIGQUERY_PROJECT
    Google Cloud project.

BIGQUERY_DATASET
    Dataset to upload into.

Defaults are intended for local development.
"""

import os
from pathlib import Path

from data_ingestion.config.schemas import (
    BUNDLE_ITEMS_SCHEMA,
    BUNDLE_PRICINGS_SCHEMA,
    BUNDLES_SCHEMA,
    CAMPAIGN_ASSIGNMENTS_SCHEMA,
    CAMPAIGN_EXPOSURES_SCHEMA,
    CAMPAIGNS_SCHEMA,
    CLICKSTREAM_SCHEMA,
    COMPETITOR_PRICE_HISTORY_SCHEMA,
    COMPETITOR_PRODUCTS_SCHEMA,
    CUSTOMERS_SCHEMA,
    INVENTORY_CHANGE_EVENTS_SCHEMA,
    PRODUCT_CONTENT_QUALITY_SCHEMA,
    PRODUCT_LIFECYCLES_SCHEMA,
    PRODUCT_REVIEWS_SCHEMA,
    PRODUCTS_SCHEMA,
    PROMOTIONS_SCHEMA,
    STOCK_SNAPSHOTS_SCHEMA,
    STOCKOUT_EVENTS_SCHEMA,
    STORE_CATALOGUES_SCHEMA,
    STORES_SCHEMA,
    TRANSACTION_ITEMS_SCHEMA,
    TRANSACTIONS_SCHEMA,
)

PROJECT_ID = os.getenv(
    "BIGQUERY_PROJECT",
    "mega-mart-storage",
)

BIGQUERY_DATASET = "synthetic_dirty"
BIGQUERY_LOCATION = "asia-southeast1"
BASE_DIR = Path(__file__).resolve().parents[2]


TABLES = {
    "customers": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/customers_dirty.csv",
        "schema": CUSTOMERS_SCHEMA,
    },
    "stores": {
        "csv": BASE_DIR / "data_generation/raw_data/stores_raw.csv",
        "schema": STORES_SCHEMA,
    },
    "products": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/products_dirty.csv",
        "schema": PRODUCTS_SCHEMA,
    },
    "store_catalogues": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/store_catalogues_dirty.csv",
        "schema": STORE_CATALOGUES_SCHEMA,
    },
    "product_lifecycles": {
        "csv": BASE_DIR / "data_generation/raw_data/product_lifecycles_raw.csv",
        "schema": PRODUCT_LIFECYCLES_SCHEMA,
    },
    "product_content_quality": {
        "csv": BASE_DIR
        / "dirty_data_generation/dirty_data/product_content_quality_dirty.csv",
        "schema": PRODUCT_CONTENT_QUALITY_SCHEMA,
    },
    "stockout_events": {
        "csv": BASE_DIR / "data_generation/raw_data/stockout_events_raw.csv",
        "schema": STOCKOUT_EVENTS_SCHEMA,
    },
    "stock_snapshots": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/stock_snapshots_dirty.csv",
        "schema": STOCK_SNAPSHOTS_SCHEMA,
    },
    "inventory_change_events": {
        "csv": BASE_DIR / "data_generation/raw_data/inventory_change_events_raw.csv",
        "schema": INVENTORY_CHANGE_EVENTS_SCHEMA,
    },
    "competitor_products": {
        "csv": BASE_DIR / "data_generation/raw_data/competitor_products_raw.csv",
        "schema": COMPETITOR_PRODUCTS_SCHEMA,
    },
    "competitor_price_history": {
        "csv": BASE_DIR
        / "dirty_data_generation/dirty_data/competitor_price_history_dirty.csv",
        "schema": COMPETITOR_PRICE_HISTORY_SCHEMA,
    },
    "campaigns": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/campaigns_dirty.csv",
        "schema": CAMPAIGNS_SCHEMA,
    },
    "campaign_assignments": {
        "csv": BASE_DIR / "data_generation/raw_data/campaign_assignments_raw.csv",
        "schema": CAMPAIGN_ASSIGNMENTS_SCHEMA,
    },
    "campaign_exposures": {
        "csv": BASE_DIR
        / "dirty_data_generation/dirty_data/campaign_exposures_dirty.csv",
        "schema": CAMPAIGN_EXPOSURES_SCHEMA,
    },
    "bundles": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/bundles_dirty.csv",
        "schema": BUNDLES_SCHEMA,
    },
    "bundle_items": {
        "csv": BASE_DIR / "data_generation/raw_data/bundle_items_raw.csv",
        "schema": BUNDLE_ITEMS_SCHEMA,
    },
    "bundle_pricings": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/bundle_pricings_dirty.csv",
        "schema": BUNDLE_PRICINGS_SCHEMA,
    },
    "promotions": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/promotions_dirty.csv",
        "schema": PROMOTIONS_SCHEMA,
    },
    "clickstreams": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/clickstreams_dirty.csv",
        "schema": CLICKSTREAM_SCHEMA,
    },
    "transactions": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/transactions_dirty.csv",
        "schema": TRANSACTIONS_SCHEMA,
    },
    "transaction_items": {
        "csv": BASE_DIR
        / "dirty_data_generation/dirty_data/transaction_items_dirty.csv",
        "schema": TRANSACTION_ITEMS_SCHEMA,
    },
    "product_reviews": {
        "csv": BASE_DIR / "dirty_data_generation/dirty_data/product_reviews_dirty.csv",
        "schema": PRODUCT_REVIEWS_SCHEMA,
    },
}
