# dirty_data_generation/corruption_rules/promotions_rules.py

import random
from datetime import timedelta

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_promotion_name(df, idx):

    df.at[idx, "promotion_name"] = None


def missing_promotion_theme(df, idx):

    df.at[idx, "promotion_theme"] = None


def missing_promotion_target_id(df, idx):
    """
    promotion_target_id is required whenever promotion_scope != 'cart'.
    """

    if pd.isna(df.at[idx, "promotion_scope"]):
        return

    if df.at[idx, "promotion_scope"] == "cart":
        return

    df.at[idx, "promotion_target_id"] = None


def missing_promotion_value(df, idx):

    df.at[idx, "promotion_value"] = None


def missing_discount_code(df, idx):

    df.at[idx, "discount_code"] = None


def missing_effective_start_date(df, idx):

    df.at[idx, "effective_start_date"] = None


def missing_effective_end_date(df, idx):

    df.at[idx, "effective_end_date"] = None


# =============================================================================
# Accepted Values
# =============================================================================


def invalid_promotion_mechanic(df, idx):

    if pd.isna(df.at[idx, "promotion_mechanic"]):
        return

    df.at[idx, "promotion_mechanic"] = random.choice(
        [
            "cashback",
            "free_gift",
            "buy_one_get_one",
            "loyalty_points",
            "",
        ]
    )


def invalid_promotion_scope(df, idx):

    if pd.isna(df.at[idx, "promotion_scope"]):
        return

    df.at[idx, "promotion_scope"] = random.choice(
        [
            "customer",
            "order",
            "brand",
            "subcategory",
            "",
        ]
    )


# =============================================================================
# Formatting
# =============================================================================


def invalid_promotion_id_format(df, idx):

    value = df.at[idx, "promotion_id"]

    if pd.isna(value):
        return

    value = str(value)

    corruptions = [
        lambda x: x.replace("000", "00", 1),
        lambda x: x.replace("PROMO", "PROMO-", 1),
        lambda x: x.lower(),
        lambda x: x.replace("PROMO", "PRO", 1),
        lambda x: x.replace("PROMO", "PROM", 1),
        lambda x: x.replace("PROMO", "PROMO_", 1),
        lambda x: x.replace("PROMO", "PROMO ", 1),
        lambda x: x.replace("PROMO", "", 1),
    ]

    df.at[idx, "promotion_id"] = random.choice(corruptions)(value)


def invalid_discount_code_format(df, idx):
    """
    discount_code must contain uppercase letters,
    numbers and underscores only.
    """

    value = df.at[idx, "discount_code"]

    if pd.isna(value):
        return

    value = str(value)

    corruptions = [
        lambda x: x.lower(),
        lambda x: x.replace("_", "-", 1),
        lambda x: x.replace("_", " ", 1),
        lambda x: x + "-",
        lambda x: x + "!",
        lambda x: x + "@",
        lambda x: " " + x,
        lambda x: x + " ",
        lambda x: x.replace("_", ".", 1),
    ]

    df.at[idx, "discount_code"] = random.choice(corruptions)(value)


# =============================================================================
# Duplicates
# =============================================================================


def duplicate_promotion_id(df, idx):

    other_promotion_ids = (
        df[df.index != idx]["promotion_id"].dropna().astype(str).tolist()
    )

    if not other_promotion_ids:
        return

    df.at[idx, "promotion_id"] = random.choice(other_promotion_ids)


# =============================================================================
# Range Validation
# =============================================================================


def promotion_value_out_of_range(df, idx):
    """
    promotion_value must be more than 0 and less than 100000.
    """

    value = df.at[idx, "promotion_value"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "promotion_value"] = random.choice(corruptions)(value)


def min_spend_out_of_range(df, idx):
    """
    min_spend must be more than 0 and less than 100000.
    """

    value = df.at[idx, "min_spend"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "min_spend"] = random.choice(corruptions)(value)


def priority_out_of_range(df, idx):
    """
    priority must be between 1 and 4 inclusive.
    """

    value = df.at[idx, "priority"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.randint(5, 10),
    ]

    df.at[idx, "priority"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def invalid_effective_period(df, idx):

    start = df.at[idx, "effective_start_date"]
    end = df.at[idx, "effective_end_date"]

    if pd.isna(start) or pd.isna(end):
        return

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    df.at[idx, "effective_start_date"] = end + timedelta(days=1)


def zero_value_non_free_shipping(df, idx):
    """
    Non-free-shipping promotions must have promotion_value > 0.

    Free shipping is intentionally excluded because 0 is valid for it.
    """

    mechanic = df.at[idx, "promotion_mechanic"]

    if pd.isna(mechanic):
        return

    if mechanic == "free_shipping":
        return

    df.at[idx, "promotion_value"] = 0.0


def free_shipping_invalid_scope(df, idx, ctx):
    """
    Free shipping promotions must use cart scope.

    We deliberately select a non cart scope and make sure the target
    remains a valid target for that scope so that the promotion
    reference tests do not fail unnecessarily.
    """

    mechanic = df.at[idx, "promotion_mechanic"]

    if pd.isna(mechanic):
        return

    # The business rule only applies to free_shipping.
    if mechanic != "free_shipping":
        return

    possible_scopes = [
        "category",
        "product",
        "bundle",
    ]

    scope = random.choice(possible_scopes)

    df.at[idx, "promotion_scope"] = scope

    # Keep target valid for the selected scope.
    if scope == "category":
        products_df = ctx.products.products_df

        categories = products_df["category"].dropna().astype(str).unique().tolist()

        if categories:
            df.at[idx, "promotion_target_id"] = random.choice(categories)

    elif scope == "product":
        products_df = ctx.products.products_df

        product_ids = products_df["product_id"].dropna().astype(str).tolist()

        if product_ids:
            df.at[idx, "promotion_target_id"] = random.choice(product_ids)

    elif scope == "bundle":
        bundle_df = ctx.bundles.bundle_full_df

        bundle_ids = bundle_df["bundle_id"].dropna().astype(str).tolist()

        if bundle_ids:
            df.at[idx, "promotion_target_id"] = random.choice(bundle_ids)


def discontinued_product_promotion_overlap(df, idx, ctx):
    """
    Promotion must not overlap a product's discontinued lifecycle.

    Selects a real discontinued product and creates a promotion period
    that overlaps its discontinued period.
    """

    if pd.isna(df.at[idx, "promotion_scope"]):
        return

    if df.at[idx, "promotion_scope"] != "product":
        return

    lifecycle_df = ctx.product_lifecycles.product_with_lifecycle_df

    if lifecycle_df.empty:
        return

    # Prefer products with an actual discontinuation date.
    discontinued = lifecycle_df[lifecycle_df["discontinuation_date"].notna()].copy()

    if discontinued.empty:
        return

    selected = discontinued.sample(1).iloc[0]

    product_id = selected["product_id"]
    discontinuation_date = pd.Timestamp(selected["discontinuation_date"])

    launch_date = selected.get("launch_date")

    if pd.isna(launch_date):
        launch_date = discontinuation_date - pd.Timedelta(days=30)
    else:
        launch_date = pd.Timestamp(launch_date)

    # Ensure a sensible lifecycle window.
    if launch_date > discontinuation_date:
        return

    overlap_type = random.choice(
        [
            "cross_boundary",
            "during_discontinued",
        ]
    )

    # Promotion starts before discontinuation and ends after it.
    if overlap_type == "cross_boundary":
        start = discontinuation_date - pd.Timedelta(days=random.randint(1, 30))
        end = discontinuation_date + pd.Timedelta(days=random.randint(1, 30))

    # Promotion occurs during discontinued period.
    else:
        start = discontinuation_date - pd.Timedelta(days=random.randint(0, 5))
        end = discontinuation_date + pd.Timedelta(days=random.randint(1, 30))

    df.at[idx, "promotion_scope"] = "product"
    df.at[idx, "promotion_target_id"] = product_id
    df.at[idx, "effective_start_date"] = start
    df.at[idx, "effective_end_date"] = end


def bundle_promotion_discount_mismatch(df, idx, ctx):
    """
    Bundle promotions must use the same discount value as the
    latest bundle pricing record.
    """

    if df.at[idx, "promotion_mechanic"] != "bundle":
        return

    if pd.isna(df.at[idx, "promotion_target_id"]):
        return

    bundle_id = df.at[idx, "promotion_target_id"]

    bundle_pricings_df = ctx.bundle_pricings.bundle_pricings_df

    pricing_rows = bundle_pricings_df[
        bundle_pricings_df["bundle_id"] == bundle_id
    ].copy()

    if pricing_rows.empty:
        return

    pricing_rows = pricing_rows[
        pricing_rows["effective_end_date"].notna()
        & pricing_rows["effective_start_date"].notna()
    ]

    if pricing_rows.empty:
        return

    latest_idx = pricing_rows.sort_values(
        ["effective_end_date", "effective_start_date"],
        ascending=False,
    ).index[0]

    latest_discount = bundle_pricings_df.at[
        latest_idx,
        "discount_value",
    ]

    if pd.isna(latest_discount):
        return

    # Ensure the corrupted value differs from the expected discount.
    corrupted_discount = round(
        float(latest_discount) + random.uniform(0.01, 10.00),
        2,
    )

    df.at[idx, "promotion_value"] = corrupted_discount
