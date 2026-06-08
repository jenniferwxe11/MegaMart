import pandas as pd

from data_generation.config.products_config import BRANDS, CATEGORIES, CATEGORY_ITEMS
from data_generation.config.store_products_config import ESSENTIAL_CATEGORIES
from data_generation.data_retrieval import load_data


def get_bundle_dict(bundle_items_df):
    return (
        bundle_items_df.groupby("bundle_id")[["product_id", "quantity"]]
        .apply(lambda df: dict(zip(df["product_id"], df["quantity"])))
        .to_dict()
    )


def get_category_to_products(products_df):
    return (
        products_df.dropna(subset=["product_id"])
        .groupby("category")["product_id"]
        .apply(list)
        .to_dict()
    )


def get_product_map(products_df):
    if products_df["product_id"].duplicated().any():
        raise ValueError("Duplicate product_id detected")
    return products_df.set_index("product_id").to_dict(orient="index")


# ─────────────────────────────────────────────────────────────
# LOOKUP MAPS
# ─────────────────────────────────────────────────────────────


def get_region_area_map():
    df = load_data.load_region_areas()
    region_area_map = df.groupby("region")["area"].apply(list).to_dict()
    return region_area_map


def get_area_region_map(region_area_map):
    area_region_map = {
        area: region for region, areas in region_area_map.items() for area in areas
    }
    return area_region_map


def get_store_maps():
    df = load_data.load_stores()
    online_rows = df[df["store_name"] == "MegaMart Online"]

    if online_rows.empty:
        raise ValueError("MegaMart Online store not found")

    online_store_id = online_rows.iloc[0]["store_id"]

    return {
        "store_ids": df["store_id"].dropna().tolist(),
        "store_area_map": df.set_index("store_id")["area"].to_dict(),
        "store_region_map": df.set_index("store_id")["region"].to_dict(),
        "online_store_id": online_store_id,
        "retail_store_ids": df.loc[
            df["store_id"].notna() & (df["store_name"] != "MegaMart Online"), "store_id"
        ].tolist(),
    }


def get_store_catalogue_maps():
    df = load_data.load_store_catalogues()

    return {
        "store_product_price_map": df.set_index(["store_id", "product_id"])[
            "store_selling_price"
        ].to_dict(),
        "store_product_name_map": df.set_index(["store_id", "product_id"])[
            "store_product_name"
        ].to_dict(),
        "store_product_category_map": df.set_index(["store_id", "product_id"])[
            "store_category"
        ].to_dict(),
    }


def get_customer_maps():
    df = load_data.load_customers()
    return {
        "customer_ids": df["customer_id"].dropna().tolist(),
        "customer_type_to_ids_map": df.groupby("customer_type")["customer_id"]
        .apply(list)
        .to_dict(),
        "customer_type_map": df.set_index("customer_id")["customer_type"].to_dict(),
        "customer_segment_map": df.set_index("customer_id")[
            "customer_segment"
        ].to_dict(),
        "customer_area_map": df.set_index("customer_id")["area"].to_dict(),
        "customer_region_map": df.set_index("customer_id")["region"].to_dict(),
    }


def get_product_maps():
    df = load_data.load_products()

    product_ids = df["product_id"].dropna().tolist()
    essential = df[df["category"].isin(ESSENTIAL_CATEGORIES)]["product_id"].tolist()
    non_essential = [pid for pid in product_ids if pid not in set(essential)]

    return {
        "product_ids": product_ids,
        "essential_product_ids": essential,
        "non_essential_product_ids": non_essential,
        "product_name_map": df.set_index("product_id")["product_name"].to_dict(),
        "product_category_map": df.set_index("product_id")["category"].to_dict(),
        "product_cost_map": df.set_index("product_id")["cost_price"].to_dict(),
        "product_price_map": df.set_index("product_id")["selling_price"].to_dict(),
    }


def get_product_lifecycle_maps():
    df = load_data.load_product_lifecycles()

    return {
        "product_launch_map": df.set_index("product_id")["launch_date"].to_dict(),
        "product_discontinuation_map": df.set_index("product_id")[
            "discontinuation_date"
        ].to_dict(),
    }


def get_stockout_event_map():
    df = load_data.load_stockout_events()

    return {
        (store_id, pid): group.reset_index(drop=True)
        for (store_id, pid), group in df.groupby(["store_id", "product_id"])
    }


def get_payment_success(clickstreams_df):

    if clickstreams_df.empty:
        return pd.DataFrame()

    if "event_type" not in clickstreams_df.columns:
        return pd.DataFrame()

    return clickstreams_df[clickstreams_df["event_type"] == "Payment Successful"]


def get_valid_transactions(transactions_df, transaction_items_df):
    if transactions_df.empty or transaction_items_df.empty:
        return pd.DataFrame()

    required_txn_cols = {
        "transaction_id",
        "customer_id",
        "transaction_time",
        "payment_method",
    }

    if not required_txn_cols.issubset(transactions_df.columns):
        return pd.DataFrame()

    if "transaction_id" not in transaction_items_df.columns:
        return pd.DataFrame()

    completed = transactions_df[list(required_txn_cols)]

    return completed.merge(transaction_items_df, on="transaction_id", how="inner")


def get_search_term():
    SEARCH_TERMS = []
    SEARCH_TERMS.extend(CATEGORIES)
    for brand_list in BRANDS.values():
        SEARCH_TERMS.extend(brand_list)
    for item_list in CATEGORY_ITEMS.values():
        SEARCH_TERMS.extend(item_list)
    return SEARCH_TERMS


def get_areas():
    LOCATIONS = load_data.load_region_areas()["area"].tolist()
    return LOCATIONS
