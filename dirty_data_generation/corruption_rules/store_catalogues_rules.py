# dirty_data_generation/corruption_rules/store_catalogues_rules.py

import random

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_store_id(df, idx):
    df.at[idx, "store_id"] = None


def missing_product_id(df, idx):
    df.at[idx, "product_id"] = None


def missing_store_product_name(df, idx):
    df.at[idx, "store_product_name"] = None


def blank_store_product_name(df, idx):
    df.at[idx, "store_product_name"] = random.choice(
        [
            "",
            " ",
            "   ",
        ]
    )


def missing_store_brand(df, idx):
    df.at[idx, "store_brand"] = None


def missing_store_category(df, idx):
    df.at[idx, "store_category"] = None


def missing_store_selling_price(df, idx):
    df.at[idx, "store_selling_price"] = None


# =============================================================================
# Range Validation
# =============================================================================


def store_selling_price_out_of_range(df, idx):
    """
    store_selling_price must be greater than 0 and less than 100000.
    """

    value = df.at[idx, "store_selling_price"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: round(random.uniform(100001, 250000), 2),
    ]

    df.at[idx, "store_selling_price"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def duplicate_store_product(df, idx):
    """
    A product must appear only once in each store's catalogue.

    Creates a duplicate (store_id, product_id) combination.
    """

    if len(df) < 2:
        return

    source_idx = random.choice(df.index.tolist())

    if source_idx == idx:
        return

    source = df.loc[source_idx]

    if pd.isna(source["store_id"]) or pd.isna(source["product_id"]):
        return

    df.at[idx, "store_id"] = source["store_id"]
    df.at[idx, "product_id"] = source["product_id"]


def store_price_product_price_mismatch(df, idx):
    """
    store_selling_price must be within 20% of the corresponding
    product selling_price.

    Creates a price outside the valid ±20% alignment range.
    """

    value = df.at[idx, "store_selling_price"]

    if pd.isna(value):
        return

    value = float(value)

    corruptions = [
        lambda x: round(x * random.uniform(0.50, 0.79), 2),
        lambda x: round(x * random.uniform(1.21, 1.50), 2),
    ]

    df.at[idx, "store_selling_price"] = random.choice(corruptions)(value)
