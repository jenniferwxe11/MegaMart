# dirty_data_generation/corruption_rules/inventory_change_events_rules.py

import random

import pandas as pd

from dirty_data_generation.helpers.dirty_utils import generate_future_datetime

# =============================================================================
# Missing Values
# =============================================================================


def missing_store_id(df, idx, ctx):

    df.at[idx, "store_id"] = None


def missing_product_id(df, idx, ctx):

    df.at[idx, "product_id"] = None


def missing_event_timestamp(df, idx, ctx):

    df.at[idx, "event_timestamp"] = None


# =============================================================================
# Accepted Values
# =============================================================================


def invalid_reason(df, idx, ctx):
    """
    reason must be one of the supported inventory change reasons.
    """

    if pd.isna(df.at[idx, "reason"]):
        return

    df.at[idx, "reason"] = random.choice(
        [
            "Unknown",
            "Manual adjustment",
            "Inventory correction",
            "Restock",
            "Damaged goods",
            "",
        ]
    )


# =============================================================================
# Range Validation
# =============================================================================


def stock_after_out_of_range(df, idx, ctx):
    """
    stock_after must be between 0 and 100000 inclusive.
    """

    value = df.at[idx, "stock_after"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.randint(100001, 250000),
    ]

    df.at[idx, "stock_after"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def future_event_timestamp(df, idx, ctx):
    """
    event_timestamp must not be in the future.
    """

    if pd.isna(df.at[idx, "event_timestamp"]):
        return

    df.at[idx, "event_timestamp"] = pd.Timestamp(generate_future_datetime())


def duplicate_inventory_change_event(df, idx, ctx):
    """
    store_id + product_id + event_timestamp must be unique.

    Copies the key fields from another event onto the current row.
    """

    key_columns = [
        "store_id",
        "product_id",
        "event_timestamp",
    ]

    other_rows = df[df.index != idx]

    if other_rows.empty:
        return

    source_idx = random.choice(other_rows.index.tolist())

    for column in key_columns:
        df.at[idx, column] = df.at[source_idx, column]


def delta_matches_stock_after_movement(df, idx, ctx):
    """
    delta must equal the change in stock_after between consecutive
    inventory change events for the same store/product.

    Deliberately changes delta without changing stock_after.
    """

    if pd.isna(df.at[idx, "delta"]):
        return

    if pd.isna(df.at[idx, "stock_after"]):
        return

    candidates = df[
        (df["store_id"] == df.at[idx, "store_id"])
        & (df["product_id"] == df.at[idx, "product_id"])
        & (df.index != idx)
    ].copy()

    if candidates.empty:
        return

    candidates["event_timestamp"] = pd.to_datetime(
        candidates["event_timestamp"],
        errors="coerce",
    )

    current_timestamp = pd.to_datetime(
        df.at[idx, "event_timestamp"],
        errors="coerce",
    )

    if pd.isna(current_timestamp):
        return

    previous = candidates[
        candidates["event_timestamp"] < current_timestamp
    ].sort_values("event_timestamp")

    if previous.empty:
        return

    previous_idx = previous.index[-1]

    expected_delta = df.at[idx, "stock_after"] - df.at[previous_idx, "stock_after"]

    # Ensure the corrupted value is actually different.
    invalid_delta = expected_delta

    while invalid_delta == expected_delta:
        invalid_delta = expected_delta + random.choice([-10, -5, -1, 1, 5, 10])

    df.at[idx, "delta"] = invalid_delta


def zero_delta(df, idx, ctx):
    """
    delta must not be zero.
    """

    if pd.isna(df.at[idx, "delta"]):
        return

    df.at[idx, "delta"] = 0


# =============================================================================
# Opening Balance Rules
# =============================================================================


def opening_balance_first_record(df, idx, ctx):
    """
    The first inventory event for every store/product must be the
    Opening balance event.

    Targets the first event for a store/product and changes its reason
    to a non-opening reason.
    """

    store_id = df.at[idx, "store_id"]
    product_id = df.at[idx, "product_id"]

    if pd.isna(store_id) or pd.isna(product_id):
        return

    group = df[(df["store_id"] == store_id) & (df["product_id"] == product_id)].copy()

    if group.empty:
        return

    group["event_timestamp"] = pd.to_datetime(
        group["event_timestamp"],
        errors="coerce",
    )

    group = group.sort_values("event_timestamp")

    first_idx = group.index[0]

    # Only corrupt the first record.
    if first_idx != idx:
        return

    non_opening_reasons = [
        "Stockout event — stock zeroed",
        "Normal healthy-band drift",
        "Low-band minor fluctuation",
        "Critical stock — replenishment triggered",
        "Forecasting error — over-ordered",
    ]

    df.at[idx, "reason"] = random.choice(non_opening_reasons)


def opening_balance_uniqueness(df, idx, ctx):
    """
    Each store/product must have exactly one Opening balance event.

    Changes a non-opening event into another Opening balance event.
    """

    store_id = df.at[idx, "store_id"]
    product_id = df.at[idx, "product_id"]

    if pd.isna(store_id) or pd.isna(product_id):
        return

    group = df[(df["store_id"] == store_id) & (df["product_id"] == product_id)].copy()

    if group.empty:
        return

    group["event_timestamp"] = pd.to_datetime(
        group["event_timestamp"],
        errors="coerce",
    )

    group = group.sort_values("event_timestamp")

    opening_rows = group[group["reason"] == "Opening balance"]

    if opening_rows.empty:
        return

    # Do not modify the existing opening balance.
    candidates = group[(group["reason"] != "Opening balance") & (group.index != idx)]

    if candidates.empty:
        return

    source_idx = random.choice(candidates.index.tolist())

    df.at[source_idx, "reason"] = "Opening balance"


def opening_balance_delta_matches_stock_after(df, idx, ctx):
    """
    Opening balance delta must equal stock_after.
    """

    if df.at[idx, "reason"] != "Opening balance":
        return

    if pd.isna(df.at[idx, "stock_after"]):
        return

    current_delta = df.at[idx, "delta"]

    if pd.isna(current_delta):
        return

    stock_after = df.at[idx, "stock_after"]

    # Ensure delta is different from stock_after.
    invalid_delta = stock_after + random.choice([-10, -1, 1, 10])

    if invalid_delta == stock_after:
        invalid_delta += 1

    df.at[idx, "delta"] = invalid_delta
