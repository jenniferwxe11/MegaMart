# dirty_data_generation/corruption_rules/bundle_pricings_rules.py

import random

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_bundle_price(df, idx, ctx):

    df.at[idx, "bundle_price"] = None


def missing_discount_value(df, idx, ctx):

    df.at[idx, "discount_value"] = None


def missing_pricing_phase(df, idx, ctx):

    df.at[idx, "pricing_phase"] = None


# =============================================================================
# Range Validation
# =============================================================================


def bundle_price_out_of_bounds(df, idx, ctx):
    """
    Bundle price should be between 0 and 100000.
    """

    value = df.at[idx, "bundle_price"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "bundle_price"] = random.choice(corruptions)(value)


def discount_value_out_of_bounds(df, idx, ctx):
    """
    Discount value should be between 0 and 100000.
    """

    value = df.at[idx, "discount_value"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "discount_value"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def end_date_before_start_date(df, idx, ctx):

    if pd.isna(df.at[idx, "effective_start_date"]) or pd.isna(
        df.at[idx, "effective_end_date"]
    ):
        return

    df.at[idx, "effective_end_date"] = df.at[
        idx, "effective_start_date"
    ] - pd.Timedelta(days=random.randint(30, 365))


def duplicate_bundle_pricing_phase(df, idx, ctx):
    """
    Each bundle should only have one pricing record for each pricing phase.
    Creates a duplicate pricing phase for the same bundle.
    """

    bundle_id = df.at[idx, "bundle_id"]

    other_rows = df[(df["bundle_id"] == bundle_id) & (df.index != idx)]

    if other_rows.empty:
        return

    other_idx = random.choice(other_rows.index.tolist())

    df.at[idx, "pricing_phase"] = df.at[other_idx, "pricing_phase"]


def discount_exceeds_bundle_price(df, idx, ctx):
    """
    discount_value must be less than or equal to bundle_price.
    """

    bundle_price = df.at[idx, "bundle_price"]

    if pd.isna(bundle_price):
        return

    if bundle_price <= 0:
        return

    # Make discount greater than bundle price.
    df.at[idx, "discount_value"] = round(
        bundle_price + random.uniform(0.01, bundle_price),
        2,
    )


def invalid_bundle_pricing_lifecycle(df, idx, ctx):
    """
    Bundle pricing phases must follow a continuous,
    chronological, non-overlapping lifecycle.
    """

    bundle_id = df.at[idx, "bundle_id"]

    other_rows = df[(df["bundle_id"] == bundle_id) & (df.index != idx)]

    if other_rows.empty:
        return

    valid_rows = other_rows[
        other_rows["effective_start_date"].notna()
        & other_rows["effective_end_date"].notna()
    ]

    if valid_rows.empty:
        return

    other_idx = random.choice(valid_rows.index.tolist())

    other_start = df.at[other_idx, "effective_start_date"]
    other_end = df.at[other_idx, "effective_end_date"]

    if other_end < other_start:
        return

    corruption = random.choice(["overlap", "gap", "invalid_period"])

    if corruption == "overlap":
        df.at[idx, "effective_start_date"] = other_start
        df.at[idx, "effective_end_date"] = other_end

    elif corruption == "gap":
        df.at[idx, "effective_start_date"] = other_end + pd.Timedelta(
            days=random.randint(2, 10)
        )
        df.at[idx, "effective_end_date"] = df.at[
            idx, "effective_start_date"
        ] + pd.Timedelta(days=random.randint(5, 30))

    else:
        df.at[idx, "effective_start_date"] = other_end
        df.at[idx, "effective_end_date"] = other_start


def bundle_pricing_phase_out_of_order(df, idx, ctx):
    """
    Pricing phases should follow:
    LAUNCH -> PROMO -> EOL.

    Corrupts a pricing phase so that its lifecycle order is invalid.
    """

    current_phase = df.at[idx, "pricing_phase"]

    if pd.isna(current_phase):
        return

    phase_corruptions = {
        "LAUNCH": ["PROMO", "EOL"],
        "PROMO": ["LAUNCH", "EOL"],
        "EOL": ["LAUNCH", "PROMO"],
    }

    possible_phases = phase_corruptions.get(current_phase)

    if not possible_phases:
        return

    df.at[idx, "pricing_phase"] = random.choice(possible_phases)


def bundle_pricing_lifecycle_gap(df, idx, ctx):
    """
    Consecutive bundle pricing phases should not contain gaps.
    Creates a gap between pricing periods.
    """

    bundle_id = df.at[idx, "bundle_id"]

    rows = df[
        (df["bundle_id"] == bundle_id)
        & df["effective_start_date"].notna()
        & df["effective_end_date"].notna()
    ].copy()

    if len(rows) < 2:
        return

    rows = rows.sort_values("effective_start_date")

    current_position = rows.index.get_loc(idx) if idx in rows.index else None

    if current_position is None or current_position == 0:
        return

    previous_idx = rows.index[current_position - 1]

    previous_end = df.at[previous_idx, "effective_end_date"]
    current_start = df.at[idx, "effective_start_date"]

    if pd.isna(previous_end) or pd.isna(current_start):
        return

    # Introduce a gap of at least one day.
    new_start = previous_end + pd.Timedelta(days=random.randint(2, 10))

    if new_start <= current_start:
        df.at[idx, "effective_start_date"] = new_start
    else:
        df.at[idx, "effective_start_date"] = current_start + pd.Timedelta(
            days=random.randint(2, 10)
        )


def bundle_price_progression_violation(df, idx, ctx):
    """
    Bundle prices should remain flat or decrease
    from LAUNCH -> PROMO -> EOL.
    """

    bundle_id = df.at[idx, "bundle_id"]

    rows = df[(df["bundle_id"] == bundle_id) & df["bundle_price"].notna()].copy()

    if len(rows) < 2:
        return

    rows["phase_order"] = rows["pricing_phase"].map(
        {
            "LAUNCH": 1,
            "PROMO": 2,
            "EOL": 3,
        }
    )

    rows = rows.sort_values("phase_order")

    if len(rows) < 2:
        return

    previous_idx = rows.index[-2]
    current_idx = rows.index[-1]

    previous_price = df.at[previous_idx, "bundle_price"]

    if pd.isna(previous_price):
        return

    df.at[current_idx, "bundle_price"] = round(
        previous_price + random.uniform(1, 10),
        2,
    )


def discount_value_progression_violation(df, idx, ctx):
    """
    Bundle discount values should remain flat or increase
    from LAUNCH -> PROMO -> EOL.
    """

    bundle_id = df.at[idx, "bundle_id"]

    rows = df[(df["bundle_id"] == bundle_id) & df["discount_value"].notna()].copy()

    if len(rows) < 2:
        return

    rows["phase_order"] = rows["pricing_phase"].map(
        {
            "LAUNCH": 1,
            "PROMO": 2,
            "EOL": 3,
        }
    )

    rows = rows.sort_values("phase_order")

    if len(rows) < 2:
        return

    previous_idx = rows.index[-2]
    current_idx = rows.index[-1]

    previous_discount = df.at[previous_idx, "discount_value"]

    if pd.isna(previous_discount):
        return

    df.at[current_idx, "discount_value"] = round(
        previous_discount - random.uniform(1, 10),
        2,
    )


def bundle_price_below_cost(df, idx, ctx):
    """
    Bundle price must be greater than or equal to the total cost
    of all products included in the bundle.
    """

    bundle_id = df.at[idx, "bundle_id"]

    if pd.isna(bundle_id):
        return

    bundle_items_df = ctx.bundles.bundle_items_df
    products_df = ctx.products.products_df

    # Get all products and quantities in this bundle
    bundle_items = bundle_items_df[bundle_items_df["bundle_id"] == bundle_id].copy()

    if bundle_items.empty:
        return

    # Join bundle items to product costs
    bundle_items = bundle_items.merge(
        products_df[["product_id", "cost_price"]],
        on="product_id",
        how="inner",
    )

    if bundle_items.empty:
        return

    # Calculate total product cost for the bundle
    total_cost = (bundle_items["cost_price"] * bundle_items["quantity"]).sum()

    if pd.isna(total_cost) or total_cost <= 0:
        return

    # Set bundle price below total product cost
    corrupted_price = total_cost * random.uniform(0.50, 0.95)

    df.at[idx, "bundle_price"] = round(corrupted_price, 2)
