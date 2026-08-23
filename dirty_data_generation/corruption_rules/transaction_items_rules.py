# dirty_data_generation/corruption_rules/transaction_items_rules.py

import random

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_transaction_id(df, idx, ctx):
    df.at[idx, "transaction_id"] = None


def missing_product_id(df, idx, ctx):
    df.at[idx, "product_id"] = None


def missing_product_name(df, idx, ctx):
    df.at[idx, "product_name"] = None


def missing_category(df, idx, ctx):
    df.at[idx, "category"] = None


def missing_quantity(df, idx, ctx):
    df.at[idx, "quantity"] = None


def missing_unit_price(df, idx, ctx):
    df.at[idx, "unit_price"] = None


def missing_item_subtotal(df, idx, ctx):
    df.at[idx, "item_subtotal"] = None


def missing_item_discount(df, idx, ctx):
    df.at[idx, "item_discount"] = None


def missing_final_item_price(df, idx, ctx):
    df.at[idx, "final_item_price"] = None


# =============================================================================
# Range Validation
# =============================================================================


def invalid_quantity(df, idx, ctx):
    """
    Quantity must be between 1 and 100000 inclusive.
    """

    value = df.at[idx, "quantity"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.randint(100001, 250000),
    ]

    df.at[idx, "quantity"] = random.choice(corruptions)(value)


def invalid_unit_price(df, idx, ctx):
    """
    Unit price must be more than 0 and less than 100000.
    """

    value = df.at[idx, "unit_price"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100000, 250000),
    ]

    df.at[idx, "unit_price"] = random.choice(corruptions)(value)


def invalid_item_subtotal(df, idx, ctx):
    """
    Item subtotal must be more than 0 and less than 100000.
    """

    value = df.at[idx, "item_subtotal"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100000, 250000),
    ]

    df.at[idx, "item_subtotal"] = random.choice(corruptions)(value)


def invalid_item_discount(df, idx, ctx):
    """
    Item discount must be between 0 and 100000 inclusive.
    """

    value = df.at[idx, "item_discount"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: -random.uniform(1, 100),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "item_discount"] = random.choice(corruptions)(value)


def invalid_final_item_price(df, idx, ctx):
    """
    Final item price must be more than 0 and less than 100000.
    """

    value = df.at[idx, "final_item_price"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100000, 250000),
    ]

    df.at[idx, "final_item_price"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def duplicate_product_in_transaction(df, idx, ctx):
    """
    Each product may only appear once per transaction.
    Copies another product_id from the same transaction.
    """

    transaction_id = df.at[idx, "transaction_id"]

    if pd.isna(transaction_id):
        return

    other_rows = df[(df["transaction_id"] == transaction_id) & (df.index != idx)]

    if other_rows.empty:
        return

    other_idx = random.choice(other_rows.index.tolist())

    df.at[idx, "product_id"] = df.at[other_idx, "product_id"]


def item_subtotal_calculation_error(df, idx, ctx):
    """
    item_subtotal must equal unit_price * quantity.
    """

    unit_price = df.at[idx, "unit_price"]
    quantity = df.at[idx, "quantity"]

    if pd.isna(unit_price) or pd.isna(quantity):
        return

    expected = round(unit_price * quantity, 2)

    df.at[idx, "item_subtotal"] = round(
        max(0.01, expected + random.choice([-1, 1]) * random.uniform(1, 20)),
        2,
    )


def item_discount_exceeds_subtotal(df, idx, ctx):
    """
    item_discount must not exceed item_subtotal.
    """

    subtotal = df.at[idx, "item_subtotal"]

    if pd.isna(subtotal) or subtotal <= 0:
        return

    df.at[idx, "item_discount"] = round(
        subtotal + random.uniform(1, max(1, subtotal * 0.5)),
        2,
    )


def final_item_price_reconciliation_error(df, idx, ctx):
    """
    final_item_price must equal item_subtotal - item_discount.
    """

    subtotal = df.at[idx, "item_subtotal"]
    discount = df.at[idx, "item_discount"]

    if pd.isna(subtotal) or pd.isna(discount):
        return

    expected = subtotal - discount

    # Keep the value positive so the range test does not mask
    # the reconciliation violation.
    df.at[idx, "final_item_price"] = round(
        max(0.01, expected + random.choice([-1, 1]) * random.uniform(1, 20)),
        2,
    )


def product_information_mismatch(df, idx, ctx):
    """
    product_name and category must match the products table.
    """

    product_id = df.at[idx, "product_id"]

    if pd.isna(product_id):
        return

    products_df = ctx.products.products_df

    product_rows = products_df[products_df["product_id"] == product_id]

    if product_rows.empty:
        return

    product = product_rows.iloc[0]

    if random.choice([True, False]):
        current_name = product["product_name"]
        df.at[idx, "product_name"] = f"{current_name} Variant"

    else:
        current_category = product["category"]

        categories = products_df["category"].dropna().unique().tolist()
        alternative_categories = [
            category for category in categories if category != current_category
        ]

        if alternative_categories:
            df.at[idx, "category"] = random.choice(alternative_categories)


def orphaned_transaction_item(df, idx, ctx):
    """
    transaction_id must exist in the transactions table.
    """

    transaction_id = df.at[idx, "transaction_id"]

    if pd.isna(transaction_id):
        return

    transactions_df = ctx.transactions.transactions_df

    if transactions_df is None or transactions_df.empty:
        return

    valid_ids = set(transactions_df["transaction_id"].dropna())

    orphan_id = f"INVALID_TRAN_{random.randint(100000, 999999)}"

    while orphan_id in valid_ids:
        orphan_id = f"INVALID_TRAN_{random.randint(100000, 999999)}"

    df.at[idx, "transaction_id"] = orphan_id
