import ast
import json
from functools import lru_cache

import pandas as pd

# ─────────────────────────────────────────────────────────────
# BASE PATH
# ─────────────────────────────────────────────────────────────

RAW_DIR = "data_generation/raw_data"

# ─────────────────────────────────────────────────────────────
# CORE LOADERS
# ─────────────────────────────────────────────────────────────


def _parse_list_col(df, col):
    def _parse(x):
        if isinstance(x, list):
            return x
        if pd.isna(x) or x == "":
            return []
        try:
            return json.loads(x)
        except Exception:
            try:
                return ast.literal_eval(x)
            except Exception:
                return []

    df[col] = df[col].apply(_parse)
    return df


@lru_cache(maxsize=None)
def _load_customers():
    return pd.read_csv(
        f"{RAW_DIR}/customers_raw.csv", parse_dates=["signup_date", "dob"]
    )


def load_customers():
    return _load_customers().copy()


@lru_cache(maxsize=None)
def _load_stores():
    return pd.read_csv(f"{RAW_DIR}/stores_raw.csv")


def load_stores():
    return _load_stores().copy()


@lru_cache(maxsize=None)
def _load_products():
    return pd.read_csv(f"{RAW_DIR}/products_raw.csv")


def load_products():
    return _load_products().copy()


def _load_competitor_products():
    return pd.read_csv(f"{RAW_DIR}/competitor_products_raw.csv")


def load_competitor_products():
    return _load_competitor_products().copy()


def _load_competitor_price_history():
    return pd.read_csv(
        f"{RAW_DIR}/competitor_price_history_raw.csv", parse_dates=["update_timestamp"]
    )


def load_competitor_price_history():
    return _load_competitor_price_history().copy()


def _load_store_catalogues():
    return pd.read_csv(f"{RAW_DIR}/store_catalogues_raw.csv")


def load_store_catalogues():
    return _load_store_catalogues().copy()


def _load_product_lifecycles():
    return pd.read_csv(
        f"{RAW_DIR}/product_lifecycles_raw.csv",
        parse_dates=["launch_date", "discontinuation_date"],
    )


def load_product_lifecycles():
    return _load_product_lifecycles().copy()


def _load_product_content_quality():
    return pd.read_csv(
        f"{RAW_DIR}/product_content_quality_raw.csv",
        parse_dates=["valid_from", "valid_to"],
    )


def load_product_content_quality():
    return _load_product_content_quality().copy()


def _load_stockout_events():
    return pd.read_csv(
        f"{RAW_DIR}/stockout_events_raw.csv",
        parse_dates=["stockout_start_date", "stockout_end_date"],
    )


def load_stockout_events():
    return _load_stockout_events().copy()


def _load_stock_snapshots():
    return pd.read_csv(
        f"{RAW_DIR}/stock_snapshots_raw.csv", parse_dates=["week_start_date"]
    )


def load_stock_snapshots():
    return _load_stock_snapshots().copy()


def _load_inventory_change_events():
    return pd.read_csv(
        f"{RAW_DIR}/inventory_change_events_raw.csv", parse_dates=["event_timestamp"]
    )


def load_inventory_change_events():
    return _load_inventory_change_events().copy()


def _load_campaigns():
    return pd.read_csv(
        f"{RAW_DIR}/campaigns_raw.csv", parse_dates=["start_date", "end_date"]
    )


def load_campaigns():
    df = _load_campaigns().copy()
    if "channels" in df.columns:
        df = _parse_list_col(df, "channels")
        return df


def _load_campaign_assignments():
    return pd.read_csv(
        f"{RAW_DIR}/campaign_assignments_raw.csv", parse_dates=["eligible_at"]
    )


def load_campaign_assignments():
    return _load_campaign_assignments().copy()


def _load_campaign_exposures():
    return pd.read_csv(
        f"{RAW_DIR}/campaign_exposures_raw.csv",
        parse_dates=["exposed_time", "opened_time", "clicked_time"],
    )


def load_campaign_exposures():
    return _load_campaign_exposures().copy()


def _load_bundles():
    return pd.read_csv(f"{RAW_DIR}/bundles_raw.csv")


def load_bundles():
    df = _load_bundles().copy()
    if "categories" in df.columns:
        df = _parse_list_col(df, "categories")
    return df


def _load_bundle_items():
    return pd.read_csv(f"{RAW_DIR}/bundle_items_raw.csv")


def load_bundle_items():
    return _load_bundle_items().copy()


def _load_bundle_pricings():
    return pd.read_csv(
        f"{RAW_DIR}/bundle_pricings_raw.csv",
        parse_dates=["effective_start_date", "effective_end_date"],
    )


def load_bundle_pricings():
    return _load_bundle_pricings().copy()


def _load_promotions():
    return pd.read_csv(
        f"{RAW_DIR}/promotions_raw.csv",
        parse_dates=["effective_start_date", "effective_end_date"],
    )


def load_promotions():
    return _load_promotions().copy()


def _load_clickstreams():
    return pd.read_csv(
        f"{RAW_DIR}/clickstreams_raw.csv", parse_dates=["event_timestamp"]
    )


def load_clickstreams():
    df = _load_clickstreams().copy()
    for col in [
        "campaign_ids",
        "promotion_ids",
        "bundle_ids",
        "cart_content",
        "purchased_items",
    ]:
        if col in df.columns:
            df = _parse_list_col(df, col)
    return df


def _load_transactions():
    return pd.read_csv(
        f"{RAW_DIR}/transactions_raw.csv", parse_dates=["transaction_time"]
    )


def load_transactions():
    df = _load_transactions().copy()
    df = _parse_list_col(df, "applied_promotions")
    return df


def _load_transaction_items():
    return pd.read_csv(f"{RAW_DIR}/transaction_items_raw.csv")


def load_transaction_items():
    return _load_transaction_items().copy()


def _load_product_reviews():
    return pd.read_csv(
        f"{RAW_DIR}/product_reviews_raw.csv", parse_dates=["review_date"]
    )


def load_product_reviews():
    return _load_product_reviews().copy()
