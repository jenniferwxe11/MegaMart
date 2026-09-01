# dirty_data_generation/corruption_rules/bundle_items_rules.py

import random

import pandas as pd

from data_generation.config.products_config import CATEGORIES

# =============================================================================
# Missing Values
# =============================================================================


def missing_quantity(df, idx, ctx):

    df.at[idx, "quantity"] = None


# =============================================================================
# Range Validation
# =============================================================================


def invalid_bundle_item_quantity(df, idx):
    """
    Bundle item quantity must be more than 0 and less than 100000.
    """
    value = df.at[idx, "quantity"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "quantity"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def duplicate_product_within_bundle(df, idx):
    """
    Each bundle-product combination should be unique.
    Creates a duplicate product within the same bundle.
    """

    bundle_id = df.at[idx, "bundle_id"]

    other_rows = df[(df["bundle_id"] == bundle_id) & (df.index != idx)]

    if other_rows.empty:
        return

    other_idx = random.choice(other_rows.index.tolist())

    df.at[idx, "product_id"] = df.at[other_idx, "product_id"]


def bundle_item_category_mismatch(df, idx, ctx):
    """
    The products assigned to a bundle should match the categories
    declared by the corresponding bundle.
    """

    bundle_id = df.at[idx, "bundle_id"]
    product_id = df.at[idx, "product_id"]

    if pd.isna(bundle_id) or pd.isna(product_id):
        return

    bundles_df = ctx.bundles.bundles_df
    products_df = ctx.products.products_df

    bundle_rows = bundles_df[bundles_df["bundle_id"] == bundle_id]

    product_rows = products_df[products_df["product_id"] == product_id]

    if bundle_rows.empty or product_rows.empty:
        return

    categories = bundle_rows.iloc[0]["categories"]

    if not categories:
        return

    # Select a category that does not belong to the bundle.
    invalid_categories = [
        category for category in CATEGORIES if category not in categories
    ]

    if not invalid_categories:
        return

    invalid_category = random.choice(invalid_categories)

    replacement_products = products_df[products_df["category"] == invalid_category][
        "product_id"
    ].tolist()

    if replacement_products:
        df.at[idx, "product_id"] = random.choice(replacement_products)


def bundle_type_quantity_mismatch(df, idx, ctx):
    """
    Quantity should be consistent with bundle type.

    Buy One, Get One -> quantity = 2
    2 For X          -> quantity = 2
    Buy N Save X     -> quantity should match N in bundle name
    """

    bundle_id = df.at[idx, "bundle_id"]

    bundles_df = ctx.bundles.bundles_df

    bundle_rows = bundles_df[bundles_df["bundle_id"] == bundle_id]

    if bundle_rows.empty:
        return

    bundle_type = bundle_rows.iloc[0]["bundle_type"]

    if bundle_type == "Buy One, Get One":
        df.at[idx, "quantity"] = random.choice([1, 3, 4])

    elif bundle_type == "2 For X":
        df.at[idx, "quantity"] = random.choice([1, 3, 4])

    elif bundle_type == "Buy N Save X":
        # Intentionally use a quantity that is different from the
        # expected purchase quantity.
        current_quantity = df.at[idx, "quantity"]

        if pd.isna(current_quantity):
            return

        df.at[idx, "quantity"] = max(
            1,
            int(current_quantity) + random.choice([-1, 1]),
        )


def bundle_type_category_mismatch(df, idx, ctx):
    """
    Non-Set bundles should use a single category.
    Set bundles may span multiple categories.
    """

    bundle_id = df.at[idx, "bundle_id"]

    bundles_df = ctx.bundles.bundles_df

    bundle_rows = bundles_df[bundles_df["bundle_id"] == bundle_id]

    if bundle_rows.empty:
        return

    bundle_type = bundle_rows.iloc[0]["bundle_type"]

    if bundle_type == "Set":
        return

    # For non-Set bundles, introduce a second category by
    # replacing the current product with one from another category.
    products_df = ctx.products.products_df

    current_product_id = df.at[idx, "product_id"]

    current_product = products_df[products_df["product_id"] == current_product_id]

    if current_product.empty:
        return

    current_category = current_product.iloc[0]["category"]

    alternative_products = products_df[products_df["category"] != current_category][
        "product_id"
    ].tolist()

    if not alternative_products:
        return

    df.at[idx, "product_id"] = random.choice(alternative_products)
