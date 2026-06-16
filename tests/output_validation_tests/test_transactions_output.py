import pandas as pd

# --- TRANSACTIONS ---


def test_transaction_time_not_in_future(dataframes):
    df = dataframes["transactions"].copy()
    assert (pd.to_datetime(df["transaction_time"]) <= pd.Timestamp.now()).all()


def test_transaction_time_after_customer_signup(dataframes):
    """
    Transaction time must not precede the customer's signup date.
    """
    transactions = dataframes["transactions"].copy()
    customers = dataframes["customers"].copy()
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


def test_transaction_total_discount_value_calculation(dataframes):
    df = dataframes["transactions"].copy()
    no_promo = df["applied_promotions"].apply(len) == 0
    assert (~no_promo | (df["total_discount"] == 0)).all()


def test_transaction_total_discount_less_than_cart_subtotal(dataframes):
    df = dataframes["transactions"].copy()
    assert (df["total_discount"] < df["cart_subtotal"]).all()


def test_transaction_shipping_discount_less_than_or_equal_to_shipping_fee(dataframes):
    df = dataframes["transactions"].copy()
    assert (df["shipping_discount"] <= df["shipping_fee"]).all()


def test_transaction_num_unique_items_less_than_or_equal_to_basket_size(dataframes):
    df = dataframes["transactions"].copy()
    assert (df["num_unique_items"] <= df["basket_size"]).all()


def test_transaction_total_calculation(dataframes):
    """
    transaction_total = cart_subtotal - total_discount + shipping_fee - shipping_discount
    """
    df = dataframes["transactions"].copy()
    expected = (
        df["cart_subtotal"]
        - df["total_discount"]
        + df["shipping_fee"]
        - df["shipping_discount"]
    ).round(2)
    actual = df["transaction_total"].round(2)
    assert (
        abs(actual - expected) < 0.02
    ).all(), "transaction_total doesn't match calculation"


# --- TRANSACTION ITEMS ---


def test_transaction_items_item_subtotal_value_calculation(dataframes):
    df = dataframes["transaction_items"].copy()
    assert (abs(df["item_subtotal"] - (df["unit_price"] * df["quantity"])) < 0.01).all()


def test_transaction_item_discount_less_than_item_subtotal(dataframes):
    df = dataframes["transaction_items"].copy()
    assert (df["item_discount"] < df["item_subtotal"]).all()


def test_transaction_item_final_price_calculation(dataframes):
    """
    final_item_price = item_subtotal - item_discount
    """
    df = dataframes["transaction_items"].copy()
    expected = (df["item_subtotal"] - df["item_discount"]).round(2)
    actual = df["final_item_price"].round(2)
    assert (
        abs(actual - expected) < 0.02
    ).all(), "final_item_price doesn't match calculation"


def test_transaction_items_subtotal_sums_to_cart_subtotal(dataframes):
    """
    Sum of final_item_price per transaction must equal cart_subtotal - shipping_fee
    """
    items = dataframes["transaction_items"].copy()
    transactions = dataframes["transactions"].copy()
    item_subtotals = items.groupby("transaction_id")["item_subtotal"].sum().round(2)
    for trans_id, item_subtotal in item_subtotals.items():
        cart_subtotal = transactions.loc[
            transactions["transaction_id"] == trans_id, "cart_subtotal"
        ].iloc[0]
        assert abs(item_subtotal - cart_subtotal) < 0.02, (
            f"cart_subtotal mismatch for transaction {trans_id}: "
            f"items item_subtotal={item_subtotal}, cart_subtotal={cart_subtotal}"
        )


def test_transaction_items_basket_size_matches_sum(dataframes):
    """
    The sum of quantities in transaction_items for a transaction must equal
    the basket_size in transactions.
    """
    items = dataframes["transaction_items"].copy()
    transactions = dataframes["transactions"].copy()
    item_totals = items.groupby("transaction_id")["quantity"].sum()
    for trans_id, total_qty in item_totals.items():
        expected = transactions.loc[
            transactions["transaction_id"] == trans_id, "basket_size"
        ].iloc[0]
        assert total_qty == expected, (
            f"basket_size mismatch for transaction {trans_id}: "
            f"items sum={total_qty}, header={expected}"
        )


def test_transaction_items_num_unique_items_matches(dataframes):
    """
    The number of distinct product_ids in transaction_items must equal
    num_unique_items in transactions.
    """
    items = dataframes["transaction_items"].copy()
    transactions = dataframes["transactions"].copy()
    unique_counts = items.groupby("transaction_id")["product_id"].nunique()
    for trans_id, count in unique_counts.items():
        expected = transactions.loc[
            transactions["transaction_id"] == trans_id, "num_unique_items"
        ].iloc[0]
        assert count == expected, (
            f"num_unique_items mismatch for transaction {trans_id}: "
            f"items={count}, header={expected}"
        )
