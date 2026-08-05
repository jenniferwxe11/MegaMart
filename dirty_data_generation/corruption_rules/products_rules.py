# dirty_data_generation/corruption_rules/products_rules.py

import random

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_product_name(df, idx, ctx):

    df.at[idx, "product_name"] = None


def missing_brand(df, idx, ctx):

    df.at[idx, "brand"] = None


def missing_category(df, idx, ctx):

    df.at[idx, "category"] = None


def missing_selling_price(df, idx, ctx):

    df.at[idx, "selling_price"] = None


def missing_cost_price(df, idx, ctx):

    df.at[idx, "cost_price"] = None


# =============================================================================
# Formatting
# =============================================================================


def invalid_product_id_format(df, idx, ctx):

    value = df.at[idx, "product_id"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: x.replace("PROD", "P"),
        lambda x: x.lower(),
        lambda x: x + "-ABC",
        lambda x: "12345",
        lambda x: "",
    ]

    df.at[idx, "product_id"] = random.choice(corruptions)(value)


def invalid_product_name_format(df, idx, ctx):

    value = df.at[idx, "product_name"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: " " + x,
        lambda x: x + " ",
        lambda x: " " + x + " ",
    ]

    df.at[idx, "product_name"] = random.choice(corruptions)(value)


# =============================================================================
# Duplicates
# =============================================================================


def duplicate_product_id(df, idx, ctx):

    product_ids = df["product_id"].dropna().tolist()

    if not product_ids:
        return

    df.at[idx, "product_id"] = random.choice(product_ids)


# =============================================================================
# Range Validation
# =============================================================================


def selling_price_out_of_bounds(df, idx, ctx):
    """
    Selling price should be between 0 and 100000.
    """

    value = df.at[idx, "selling_price"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: 0,
        lambda x: x * -1,
        lambda x: x + random.uniform(100000, 10000000),
    ]

    df.at[idx, "selling_price"] = random.choice(corruptions)(value)


def cost_price_out_of_bounds(df, idx, ctx):
    """
    Cost price should be between 0 and 100000.
    """

    value = df.at[idx, "cost_price"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: 0,
        lambda x: x * -1,
        lambda x: x + random.uniform(100000, 10000000),
    ]

    df.at[idx, "cost_price"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def cost_price_greater_than_selling_price(df, idx, ctx):
    """
    Cost price is greater than selling price.
    """

    if pd.isna(df.at[idx, "cost_price"]) or pd.isna(df.at[idx, "selling_price"]):
        return

    df.at[idx, "cost_price"] = df.at[idx, "selling_price"] + random.uniform(1, 100)
