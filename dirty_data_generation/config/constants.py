RAW_DIR = "data_generation/raw_data"
DIRTY_DIR = "dirty_data_generation/dirty_data"
MAX_ERRORS_PER_ROW = 4

DIRTY_PLAN = {
    "customers_raw.csv": "dirty_customers",
    "products_raw.csv": "dirty_products",
    "competitor_price_history_raw.csv": "dirty_competitor_products",
    "store_catalogues_raw.csv": "dirty_store_catalogues",
    "product_content_quality_raw.csv": "dirty_product_content",
    "stock_snapshots_raw.csv": "dirty_stock_snapshots",
    "campaigns_raw.csv": "dirty_campaigns",
    "campaign_exposures_raw.csv": "dirty_campaign_exposures",
    "bundles_raw.csv": "dirty_bundles",
    "bundle_pricings_raw.csv": "dirty_bundle_pricings",
    "promotions_raw.csv": "dirty_promotions",
    "clickstreams_raw.csv": "dirty_clickstreams",
    "transactions_raw.csv": "dirty_transactions",
    "transaction_items_raw.csv": "dirty_transaction_items",
    "product_reviews_raw.csv": "dirty_reviews",
}


CLEAN_TABLES = [
    "stores_raw.csv",  # Small, human-curated master
    "competitor_catalog_raw.csv",  # Product listing catalogue — kept clean
    "product_lifecycles_raw.csv",  # System-generated, deterministic
    "stockout_events_raw.csv",  # Operational event log — kept clean
    "campaign_assignments_raw.csv",  # Deterministic system output
    "bundle_items_raw.csv",  # Pure join table, no free-text
    "inventory_change_events_raw.csv",
]


DUP_PROB = {
    "clean": 0.01,
    "light_noise": 0.03,
    "moderate_noise": 0.08,
    "heavy_corruption": 0.15,
}


BOT_PROB = {
    "clean": 0.0,
    "light_noise": 0.01,
    "moderate_noise": 0.12,
    "heavy_corruption": 0.25,
}
