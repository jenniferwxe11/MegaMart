import pandas as pd

from data_generation.config.constants import DATA_END_DATE, DATA_START_DATE

# --- TRANSACTIONS ---


def test_transaction_output_time_within_data_window(ctx):
    df = ctx.transactions.transactions_df
    start = pd.Timestamp(DATA_START_DATE)
    end = pd.Timestamp(DATA_END_DATE) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    ts = pd.to_datetime(df["transaction_time"])
    assert (ts <= end).all()
    assert (ts >= start).all()


def test_transaction_output_time_not_in_future(ctx):
    df = ctx.transactions.transactions_df
    assert (pd.to_datetime(df["transaction_time"]) <= pd.Timestamp.now()).all()


def test_transaction_output_time_after_customer_signup(ctx):
    """
    Transaction time must not precede the customer's signup date.
    """
    transactions = ctx.transactions.transactions_df
    customers = ctx.customers.customers_df
    merged = transactions.merge(
        customers[["customer_id", "signup_date"]],
        on="customer_id",
        how="left",
    )
    mask = merged["signup_date"].notna()
    sub = merged[mask]
    assert (
        pd.to_datetime(sub["transaction_time"]) >= pd.to_datetime(sub["signup_date"])
    ).all(), "Transaction time is before customer signup date"


def test_transaction_output_total_discount_value_calculation(ctx):
    df = ctx.transactions.transactions_df
    no_promo = df["applied_promotions"].apply(len) == 0
    assert (~no_promo | (df["total_discount"] == 0)).all()


def test_transaction_output_total_discount_less_than_cart_subtotal(ctx):
    df = ctx.transactions.transactions_df
    assert (df["total_discount"] < df["cart_subtotal"]).all()


def test_transaction_output_shipping_discount_less_than_or_equal_to_shipping_fee(ctx):
    df = ctx.transactions.transactions_df
    assert (df["shipping_discount"] <= df["shipping_fee"]).all()


def test_transaction_output_num_unique_items_less_than_or_equal_to_basket_size(ctx):
    df = ctx.transactions.transactions_df
    assert (df["num_unique_items"] <= df["basket_size"]).all()


def test_transaction_output_total_calculation(ctx):
    """
    transaction_total = cart_subtotal - total_discount + shipping_fee - shipping_discount
    """
    df = ctx.transactions.transactions_df
    expected = (
        df["cart_subtotal"]
        - df["total_discount"]
        + df["shipping_fee"]
        - df["shipping_discount"]
    ).round(2)

    actual = df["transaction_total"].round(2)

    diff = (actual - expected).abs()

    mask = diff >= 0.02
    failed = df.loc[mask].copy()
    failed["expected"] = expected[mask]
    failed["actual"] = actual[mask]
    failed["diff"] = diff[mask]

    assert failed.empty, f"\n{failed}"


# --- TRANSACTION ITEMS ---


def test_transaction_output_items_item_subtotal_value_calculation(ctx):
    df = ctx.transactions.transaction_items_df
    assert (abs(df["item_subtotal"] - (df["unit_price"] * df["quantity"])) < 0.01).all()


def test_transaction_output_item_discount_less_than_item_subtotal(ctx):
    df = ctx.transactions.transaction_items_df
    assert (df["item_discount"] < df["item_subtotal"]).all()


def test_transaction_output_item_final_price_calculation(ctx):
    """
    final_item_price = item_subtotal - item_discount
    """
    df = ctx.transactions.transaction_items_df
    expected = (df["item_subtotal"] - df["item_discount"]).round(2)
    actual = df["final_item_price"].round(2)
    assert (
        abs(actual - expected) < 0.02
    ).all(), "final_item_price doesn't match calculation"


def test_transaction_output_items_subtotal_sums_to_cart_subtotal(ctx):
    """
    Sum of final_item_price per transaction must equal cart_subtotal - shipping_fee
    """
    items = ctx.transactions.transaction_items_df
    transactions = ctx.transactions.transactions_df
    item_subtotals = items.groupby("transaction_id")["item_subtotal"].sum().round(2)
    for trans_id, item_subtotal in item_subtotals.items():
        cart_subtotal = transactions.loc[
            transactions["transaction_id"] == trans_id, "cart_subtotal"
        ].iloc[0]
        assert abs(item_subtotal - cart_subtotal) < 0.02, (
            f"cart_subtotal mismatch for transaction {trans_id}: "
            f"items item_subtotal={item_subtotal}, cart_subtotal={cart_subtotal}"
        )


def test_transaction_output_items_basket_size_matches_sum(ctx):
    """
    The sum of quantities in transaction_items for a transaction must equal
    the basket_size in transactions.
    """
    items = ctx.transactions.transaction_items_df
    transactions = ctx.transactions.transactions_df
    item_totals = items.groupby("transaction_id")["quantity"].sum()
    for trans_id, total_qty in item_totals.items():
        expected = transactions.loc[
            transactions["transaction_id"] == trans_id, "basket_size"
        ].iloc[0]
        assert total_qty == expected, (
            f"basket_size mismatch for transaction {trans_id}: "
            f"items sum={total_qty}, header={expected}"
        )


def test_transaction_output_items_num_unique_items_matches(ctx):
    """
    The number of distinct product_ids in transaction_items must equal
    num_unique_items in transactions.
    """
    items = ctx.transactions.transaction_items_df
    transactions = ctx.transactions.transactions_df
    unique_counts = items.groupby("transaction_id")["product_id"].nunique()
    for trans_id, count in unique_counts.items():
        expected = transactions.loc[
            transactions["transaction_id"] == trans_id, "num_unique_items"
        ].iloc[0]
        assert count == expected, (
            f"num_unique_items mismatch for transaction {trans_id}: "
            f"items={count}, header={expected}"
        )
