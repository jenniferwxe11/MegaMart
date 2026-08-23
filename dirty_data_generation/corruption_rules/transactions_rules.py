# dirty_data_generation/corruption_rules/transactions_rules.py

import random

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_transaction_id(df, idx, ctx):
    df.at[idx, "transaction_id"] = None


def missing_customer_id(df, idx, ctx):
    df.at[idx, "customer_id"] = None


def missing_store_id(df, idx, ctx):
    df.at[idx, "store_id"] = None


def missing_transaction_time(df, idx, ctx):
    df.at[idx, "transaction_time"] = None


def missing_cart_subtotal(df, idx, ctx):
    df.at[idx, "cart_subtotal"] = None


def missing_total_discount(df, idx, ctx):
    df.at[idx, "total_discount"] = None


def missing_shipping_fee(df, idx, ctx):
    df.at[idx, "shipping_fee"] = None


def missing_shipping_discount(df, idx, ctx):
    df.at[idx, "shipping_discount"] = None


def missing_transaction_total(df, idx, ctx):
    df.at[idx, "transaction_total"] = None


def missing_payment_method(df, idx, ctx):
    df.at[idx, "payment_method"] = None


def missing_basket_size(df, idx, ctx):
    df.at[idx, "basket_size"] = None


def missing_num_unique_items(df, idx, ctx):
    df.at[idx, "num_unique_items"] = None


# =============================================================================
# Formatting
# =============================================================================


def invalid_transaction_id_format(df, idx, ctx):
    """
    Transaction ID must follow TRAN followed by at least three digits.
    """
    value = df.at[idx, "transaction_id"]

    if pd.isna(value):
        return

    invalid_values = [
        f"TRX{str(value).replace('TRAN', '')}",
        f"{value}_X",
        str(value).replace("TRAN", "transaction_"),
        f"INVALID_{value}",
    ]

    df.at[idx, "transaction_id"] = random.choice(invalid_values)


# =============================================================================
# Range Validation
# =============================================================================


def invalid_cart_subtotal(df, idx, ctx):
    """
    Cart subtotal must be more than 0 and less than 100000.
    """
    value = df.at[idx, "cart_subtotal"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100000, 250000),
    ]

    df.at[idx, "cart_subtotal"] = random.choice(corruptions)(value)


def invalid_total_discount(df, idx, ctx):
    """
    Total discount must be between 0 and 100000 inclusive.
    """
    value = df.at[idx, "total_discount"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: -random.uniform(1, 100),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "total_discount"] = random.choice(corruptions)(value)


def invalid_shipping_fee(df, idx, ctx):
    """
    Shipping fee must be between 0 and 100000 inclusive.
    """
    value = df.at[idx, "shipping_fee"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: -random.uniform(1, 100),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "shipping_fee"] = random.choice(corruptions)(value)


def invalid_shipping_discount(df, idx, ctx):
    """
    Shipping discount must be between 0 and 100000 inclusive.
    """
    value = df.at[idx, "shipping_discount"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: -random.uniform(1, 100),
        lambda _: random.uniform(100001, 250000),
    ]

    df.at[idx, "shipping_discount"] = random.choice(corruptions)(value)


def invalid_transaction_total(df, idx, ctx):
    """
    Transaction total must be more than 0 and less than 100000.
    """
    value = df.at[idx, "transaction_total"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100000, 250000),
    ]

    df.at[idx, "transaction_total"] = random.choice(corruptions)(value)


def invalid_basket_size(df, idx, ctx):
    """
    Basket size must be between 1 and 100000 inclusive.
    """
    value = df.at[idx, "basket_size"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.randint(100001, 250000),
    ]

    df.at[idx, "basket_size"] = random.choice(corruptions)(value)


def invalid_num_unique_items(df, idx, ctx):
    """
    Number of unique items must be between 1 and 100000 inclusive.
    """
    value = df.at[idx, "num_unique_items"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.randint(100001, 250000),
    ]

    df.at[idx, "num_unique_items"] = random.choice(corruptions)(value)


# =============================================================================
# Data Quality
# =============================================================================


def invalid_payment_method(df, idx, ctx):
    """
    Payment method must be one of the supported payment methods.
    """
    value = df.at[idx, "payment_method"]

    if pd.isna(value):
        return

    df.at[idx, "payment_method"] = random.choice(
        [
            "Bitcoin",
            "Cheque",
            "Bank Transfer",
            "Unknown",
            "Invalid Payment",
        ]
    )


# =============================================================================
# Date Issues
# =============================================================================


def future_transaction_time(df, idx, ctx):
    """
    Transaction time must not be in the future.
    """
    value = df.at[idx, "transaction_time"]

    if pd.isna(value):
        return

    df.at[idx, "transaction_time"] = (
        pd.Timestamp.now().normalize()
        + pd.Timedelta(days=random.randint(1, 365))
        + pd.Timedelta(hours=random.randint(1, 23))
    )


# =============================================================================
# Business Rule Violations
# =============================================================================


def duplicate_transaction_id(df, idx, ctx):
    """
    Transaction ID must be unique.
    """

    value = df.at[idx, "transaction_id"]

    if pd.isna(value):
        return

    other_rows = df[(df.index != idx) & df["transaction_id"].notna()]

    if other_rows.empty:
        return

    other_idx = random.choice(other_rows.index.tolist())

    df.at[idx, "transaction_id"] = df.at[other_idx, "transaction_id"]


def duplicate_transaction(df, idx, ctx):
    """
    Each customer/store/timestamp combination should be unique.

    Copies the customer, store and transaction timestamp from another
    transaction while retaining the current transaction_id.
    """

    if len(df) < 2:
        return

    other_rows = df[df.index != idx]

    if other_rows.empty:
        return

    other_idx = random.choice(other_rows.index.tolist())

    df.at[idx, "customer_id"] = df.at[other_idx, "customer_id"]
    df.at[idx, "store_id"] = df.at[other_idx, "store_id"]
    df.at[idx, "transaction_time"] = df.at[other_idx, "transaction_time"]


def transaction_without_items(df, idx, ctx):
    """
    Removes the transaction's corresponding items from transaction_items.
    """

    transaction_id = df.at[idx, "transaction_id"]

    if pd.isna(transaction_id):
        return

    transaction_items_df = ctx.transactions.transaction_items_df

    if transaction_items_df is None or transaction_items_df.empty:
        return

    transaction_items_df.drop(
        transaction_items_df[
            transaction_items_df["transaction_id"] == transaction_id
        ].index,
        inplace=True,
    )


def basket_size_mismatch(df, idx, ctx):
    """
    basket_size must equal the total quantity of transaction items.
    """

    transaction_id = df.at[idx, "transaction_id"]

    if pd.isna(transaction_id):
        return

    transaction_items_df = ctx.transactions.transaction_items_df

    if transaction_items_df is None:
        return

    items = transaction_items_df[
        transaction_items_df["transaction_id"] == transaction_id
    ]

    if items.empty:
        return

    actual_basket_size = items["quantity"].sum()

    if pd.isna(actual_basket_size):
        return

    df.at[idx, "basket_size"] = int(actual_basket_size) + random.randint(1, 20)


def num_unique_items_mismatch(df, idx, ctx):
    """
    num_unique_items must equal the number of unique products
    in transaction_items.
    """

    transaction_id = df.at[idx, "transaction_id"]

    if pd.isna(transaction_id):
        return

    transaction_items_df = ctx.transactions.transaction_items_df

    if transaction_items_df is None:
        return

    items = transaction_items_df[
        transaction_items_df["transaction_id"] == transaction_id
    ]

    if items.empty:
        return

    actual_count = items["product_id"].nunique()

    if actual_count == 0:
        return

    if actual_count == 1:
        invalid_value = 2
    else:
        invalid_value = random.choice(
            [
                actual_count - 1,
                actual_count + 1,
            ]
        )

    df.at[idx, "num_unique_items"] = invalid_value


def transaction_discount_mismatch(df, idx, ctx):
    """
    total_discount must equal the sum of item_discount values.
    """

    transaction_id = df.at[idx, "transaction_id"]

    if pd.isna(transaction_id):
        return

    transaction_items_df = ctx.transactions.transaction_items_df

    if transaction_items_df is None:
        return

    items = transaction_items_df[
        transaction_items_df["transaction_id"] == transaction_id
    ]

    if items.empty:
        return

    actual_discount = round(items["item_discount"].sum(), 2)

    df.at[idx, "total_discount"] = round(
        max(0, actual_discount + random.uniform(1, 20)),
        2,
    )


def total_discount_exceeds_subtotal(df, idx, ctx):
    """
    total_discount must not exceed cart_subtotal.
    """

    subtotal = df.at[idx, "cart_subtotal"]

    if pd.isna(subtotal):
        return

    if subtotal <= 0:
        return

    df.at[idx, "total_discount"] = round(
        subtotal + random.uniform(1, max(1, subtotal * 0.5)),
        2,
    )


def shipping_discount_without_fee(df, idx, ctx):
    """
    shipping_discount must be zero when shipping_fee is zero.
    """

    shipping_fee = df.at[idx, "shipping_fee"]

    if pd.isna(shipping_fee):
        return

    if shipping_fee != 0:
        return

    df.at[idx, "shipping_discount"] = round(
        random.uniform(1, 20),
        2,
    )


def shipping_discount_not_equal_fee(df, idx, ctx):
    """
    Shipping discount must either be zero or equal to shipping_fee.
    """

    shipping_fee = df.at[idx, "shipping_fee"]

    if pd.isna(shipping_fee) or shipping_fee <= 0:
        return

    df.at[idx, "shipping_discount"] = round(
        shipping_fee * random.choice([0.25, 0.5, 0.75]),
        2,
    )


def applied_promotions_discount_mismatch(df, idx, ctx):
    """
    Creates a mismatch between discounts and applied_promotions.

    If discounts exist, remove the promotion array.
    If no discounts exist, add a promotion entry.
    """

    total_discount = df.at[idx, "total_discount"]
    shipping_discount = df.at[idx, "shipping_discount"]

    if pd.isna(total_discount) or pd.isna(shipping_discount):
        return

    has_discount = total_discount + shipping_discount > 0

    if has_discount:
        df.at[idx, "applied_promotions"] = []

    else:
        promotions_df = ctx.promotions.promotions_df

        if promotions_df.empty:
            return

        promotion_id = random.choice(promotions_df["promotion_id"].dropna().tolist())

        promotion = promotions_df[promotions_df["promotion_id"] == promotion_id].iloc[0]

        df.at[idx, "applied_promotions"] = [
            {
                "promotion_id": promotion_id,
                "promotion_type": promotion["promotion_mechanic"],
                "amount": 5.0,
            }
        ]


def transaction_total_reconciliation_error(df, idx, ctx):
    """
    transaction_total must reconcile with cart subtotal, discounts,
    and shipping.
    """

    cart_subtotal = df.at[idx, "cart_subtotal"]
    total_discount = df.at[idx, "total_discount"]
    shipping_fee = df.at[idx, "shipping_fee"]
    shipping_discount = df.at[idx, "shipping_discount"]

    if any(
        pd.isna(value)
        for value in [
            cart_subtotal,
            total_discount,
            shipping_fee,
            shipping_discount,
        ]
    ):
        return

    expected_total = cart_subtotal - total_discount + shipping_fee - shipping_discount

    df.at[idx, "transaction_total"] = round(
        max(0.01, expected_total + random.choice([-1, 1]) * random.uniform(1, 20)),
        2,
    )


def unique_items_exceed_basket_size(df, idx, ctx):
    """
    num_unique_items must not exceed basket_size.
    """

    basket_size = df.at[idx, "basket_size"]

    if pd.isna(basket_size) or basket_size < 1:
        return

    df.at[idx, "num_unique_items"] = int(basket_size) + random.randint(1, 10)


# =============================================================================
# Applied Promotions
# =============================================================================


def _get_applied_promotions(df, idx):
    promotions = df.at[idx, "applied_promotions"]

    if not isinstance(promotions, list) or not promotions:
        return None

    return promotions


def missing_applied_promotion_id(df, idx, ctx):
    promotions = _get_applied_promotions(df, idx)

    if promotions is None:
        return

    promotion = random.choice(promotions)

    if isinstance(promotion, dict):
        promotion["promotion_id"] = None


def missing_applied_promotion_type(df, idx, ctx):
    promotions = _get_applied_promotions(df, idx)

    if promotions is None:
        return

    promotion = random.choice(promotions)

    if isinstance(promotion, dict):
        promotion["promotion_type"] = None


def missing_applied_promotion_amount(df, idx, ctx):
    promotions = _get_applied_promotions(df, idx)

    if promotions is None:
        return

    promotion = random.choice(promotions)

    if isinstance(promotion, dict):
        promotion["amount"] = None


def invalid_applied_promotion_amount(df, idx, ctx):
    """
    Promotion amount must be more than 0 and less than 100000.
    """

    promotions = _get_applied_promotions(df, idx)

    if promotions is None:
        return

    promotion = random.choice(promotions)

    if not isinstance(promotion, dict):
        return

    value = promotion.get("amount")

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100000, 250000),
    ]

    promotion["amount"] = random.choice(corruptions)(value)


def duplicate_applied_promotion(df, idx, ctx):
    """
    A promotion may only appear once per transaction.
    """

    promotions = _get_applied_promotions(df, idx)

    if promotions is None:
        return

    valid_promotions = [
        promotion
        for promotion in promotions
        if isinstance(promotion, dict) and promotion.get("promotion_id") is not None
    ]

    if not valid_promotions:
        return

    promotion = random.choice(valid_promotions)

    promotions.append(promotion.copy())


def applied_promotion_type_mismatch(df, idx, ctx):
    """
    promotion_type must match promotion_mechanic in promotions.
    """

    promotions = _get_applied_promotions(df, idx)

    if promotions is None:
        return

    promotions_df = ctx.promotions.promotions_df

    if promotions_df is None or promotions_df.empty:
        return

    valid_promotions = [
        value
        for value in promotions
        if isinstance(value, dict) and value.get("promotion_id") is not None
    ]

    if not valid_promotions:
        return

    promotion = random.choice(valid_promotions)

    promotion_id = promotion.get("promotion_id")

    promotion_rows = promotions_df[promotions_df["promotion_id"] == promotion_id]

    if promotion_rows.empty:
        return

    expected_type = promotion_rows.iloc[0]["promotion_mechanic"]

    alternative_types = [
        value
        for value in promotions_df["promotion_mechanic"].dropna().unique().tolist()
        if value != expected_type
    ]

    if not alternative_types:
        return

    promotion["promotion_type"] = random.choice(alternative_types)
