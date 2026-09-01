# dirty_data_generation/corruption_rules/stock_snapshots_rules.py

import random
from datetime import timedelta

import pandas as pd

from dirty_data_generation.helpers.dirty_utils import generate_future_datetime

# =============================================================================
# Missing Values
# =============================================================================


def missing_week_start_date(df, idx):

    df.at[idx, "week_start_date"] = None


def missing_store_id(df, idx):

    df.at[idx, "store_id"] = None


def missing_product_id(df, idx):

    df.at[idx, "product_id"] = None


def missing_stock_status(df, idx):

    df.at[idx, "stock_status"] = None


def missing_stock_band(df, idx):

    df.at[idx, "stock_band"] = None


# =============================================================================
# Accepted Values
# =============================================================================


def invalid_stock_status(df, idx):

    if pd.isna(df.at[idx, "stock_status"]):
        return

    df.at[idx, "stock_status"] = random.choice(
        [
            "Available",
            "Unavailable",
            "Critical",
            "Normal",
            "Excess",
            "",
        ]
    )


def invalid_stock_band(df, idx):

    if pd.isna(df.at[idx, "stock_band"]):
        return

    df.at[idx, "stock_band"] = random.choice(
        [
            "1",
            "5-10",
            "20-50",
            "100-200",
            "Unknown",
            "",
        ]
    )


# =============================================================================
# Business Rule Violations
# =============================================================================


def future_week_start_date(df, idx):

    if pd.isna(df.at[idx, "week_start_date"]):
        return

    df.at[idx, "week_start_date"] = pd.Timestamp(generate_future_datetime())


def duplicate_stock_snapshot(df, idx):

    key_columns = [
        "week_start_date",
        "store_id",
        "product_id",
    ]

    other_rows = df[df.index != idx]

    if other_rows.empty:
        return

    source_idx = random.choice(other_rows.index.tolist())

    for column in key_columns:
        df.at[idx, column] = df.at[source_idx, column]


def snapshot_outside_product_lifecycle(df, idx, ctx):
    """
    Snapshot week_start_date must fall within the product's active lifecycle.
    """

    if ctx.product_lifecycles is None:
        return

    product_id = df.at[idx, "product_id"]
    week_start_date = df.at[idx, "week_start_date"]

    if pd.isna(product_id) or pd.isna(week_start_date):
        return

    lifecycles = ctx.product_lifecycles.product_lifecycles_df

    matches = lifecycles[lifecycles["product_id"] == product_id]

    if matches.empty:
        return

    lifecycle = random.choice(matches.to_dict("records"))

    valid_from = lifecycle["valid_from"]
    valid_to = lifecycle["valid_to"]

    if pd.isna(valid_from):
        return

    valid_from = pd.Timestamp(valid_from)

    # -------------------------------------------------------------------------
    # Option 1:
    # Move snapshot before lifecycle start.
    # -------------------------------------------------------------------------

    before_start = valid_from - timedelta(days=random.randint(1, 90))

    # -------------------------------------------------------------------------
    # Option 2:
    # If lifecycle has ended, move snapshot after valid_to.
    # -------------------------------------------------------------------------

    if not pd.isna(valid_to):
        valid_to = pd.Timestamp(valid_to)

        after_end = valid_to + timedelta(days=random.randint(1, 90))

        if random.choice([True, False]):
            df.at[idx, "week_start_date"] = after_end
            return

    df.at[idx, "week_start_date"] = before_start


def no_consecutive_duplicate_status(df, idx):
    """
    Copies the previous snapshot's stock classification onto the current
    snapshot for the same store/product.
    """

    candidates = df[
        (df["store_id"] == df.at[idx, "store_id"])
        & (df["product_id"] == df.at[idx, "product_id"])
        & (df.index != idx)
    ].copy()

    if candidates.empty:
        return

    candidates["week_start_date"] = pd.to_datetime(
        candidates["week_start_date"],
        errors="coerce",
    )

    if pd.isna(df.at[idx, "week_start_date"]):
        return

    current_date = pd.Timestamp(df.at[idx, "week_start_date"])

    previous = candidates[candidates["week_start_date"] < current_date].sort_values(
        "week_start_date"
    )

    if previous.empty:
        return

    previous_idx = previous.index[-1]

    df.at[idx, "stock_band"] = df.at[previous_idx, "stock_band"]
    df.at[idx, "stock_status"] = df.at[previous_idx, "stock_status"]


def invalid_stock_band_status_combination(df, idx):
    """
    stock_band and stock_status must represent the same inventory level.

    Valid combinations:

        0       -> Out of Stock
        1-5     -> Limited Stock
        6-20    -> Low Stock
        21-100  -> In Stock
        101+    -> Overstocked
    """

    stock_band = df.at[idx, "stock_band"]

    if pd.isna(stock_band):
        return

    valid_statuses = {
        "0": "Out of Stock",
        "1-5": "Limited Stock",
        "6-20": "Low Stock",
        "21-100": "In Stock",
        "101+": "Overstocked",
    }

    if stock_band not in valid_statuses:
        return

    correct_status = valid_statuses[stock_band]

    invalid_statuses = [
        status for status in valid_statuses.values() if status != correct_status
    ]

    df.at[idx, "stock_status"] = random.choice(invalid_statuses)


# =============================================================================
# Cross-Entity Consistency
# =============================================================================


def store_product_snapshot_mismatch(df, idx, ctx):
    """
    store_id + product_id should represent a valid store-product catalogue
    combination.

    This catches snapshots for products that are not actually carried by
    the store.
    """

    if ctx.store_catalogues is None:
        return

    store_id = df.at[idx, "store_id"]
    product_id = df.at[idx, "product_id"]

    if pd.isna(store_id) or pd.isna(product_id):
        return

    catalogues = ctx.store_catalogues.store_catalogues_df

    if catalogues.empty:
        return

    valid_pairs = set(
        zip(
            catalogues["store_id"],
            catalogues["product_id"],
        )
    )

    current_pair = (
        store_id,
        product_id,
    )

    if current_pair not in valid_pairs:
        return

    # Find another product that this store does not carry.
    store_products = set(
        catalogues.loc[
            catalogues["store_id"] == store_id,
            "product_id",
        ].dropna()
    )

    all_products = set(ctx.products.products_df["product_id"].dropna())

    invalid_products = list(all_products - store_products)

    if not invalid_products:
        return

    df.at[idx, "product_id"] = random.choice(invalid_products)
