import random

import numpy as np
import pandas as pd
from faker import Faker

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    inject_nulls,
)
from dirty_data_generation.utils.io_utils import save

fake = Faker()


@register("dirty_transactions")
def dirty_transactions(ctx: GenerationContext):
    df = ctx.transactions.transactions_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    for i, row in df.iterrows():
        expected_total = (
            row["cart_subtotal"]
            - row.get("total_discount", 0)
            + row.get("shipping_fee", 0)
            - row.get("shipping_discount", 0)
        )
        if abs(expected_total - row["transaction_total"]) > 0.02:
            df.at[i, "error_types"].append("calculation mismatch")

    # total ≠ subtotal - discount + shipping
    math_idx = df.sample(frac=0.05, random_state=50).index
    df.loc[math_idx, "transaction_total"] = [
        round(total + random.uniform(-50, 50), 2)
        for total in df.loc[math_idx, "transaction_total"]
    ]
    append_error(
        df,
        math_idx,
        error_label="calculation error",
        columns=[
            "transaction_total",
            "cart_subtotal",
            "total_discount",
            "shipping_fee",
            "shipping_discount",
        ],
    )

    # Negative transaction_total for Completed orders
    neg_idx = df.sample(frac=0.02, random_state=51).index
    df.loc[neg_idx, "transaction_total"] = -abs(df.loc[neg_idx, "transaction_total"])
    append_error(
        df,
        neg_idx,
        error_label="negative transaction total",
        columns=["transaction_total"],
    )

    # Missing customer_id
    df = inject_nulls(
        df,
        df["customer_id"].isna(),
        "customer_id",
        rate=0.03,
        error_label="missing customer ID",
    )

    # Duplicate transaction_id
    dup_idx = df.sample(frac=0.02, random_state=52).index
    replacement_ids = (
        df["transaction_id"]
        .sample(n=len(dup_idx), replace=True, random_state=25)
        .values
    )
    df.loc[dup_idx, "transaction_id"] = replacement_ids
    append_error(
        df,
        dup_idx,
        error_label="duplicate transaction id",
        columns=["transaction_id"],
    )

    # cart_subtotal = 0 for Completed order
    zero_idx = df.sample(frac=0.02, random_state=53).index
    df.loc[zero_idx, "cart_subtotal"] = 0.0
    append_error(
        df,
        zero_idx,
        error_label="zero cart subtotal for completed order",
        columns=["cart_subtotal"],
    )

    # basket_size mismatch
    mismatch_idx = df.sample(frac=0.03, random_state=54).index
    df.loc[mismatch_idx, "basket_size"] = (
        df.loc[mismatch_idx, "basket_size"]
        + np.random.randint(-5, 6, size=len(mismatch_idx))
    ).clip(lower=0)
    append_error(
        df,
        mismatch_idx,
        error_label="basket size mismatch",
        columns=["basket_size", "transaction_id"],
    )

    # Invalid payment_method value
    pm_idx = df[df["payment_method"].notna()].sample(frac=0.02, random_state=55).index
    df.loc[pm_idx, "payment_method"] = [
        random.choice(["Bitcoin", "Barter", "Gift Card", "UNKNOWN"])
        for _ in range(len(pm_idx))
    ]
    append_error(
        df,
        pm_idx,
        error_label="invalid payment method",
        columns=["payment_method"],
    )

    # Future transaction_time
    fut_idx = (
        df[df["transaction_time"].notna()].sample(frac=0.01, random_state=57).index
    )
    df.loc[fut_idx, "transaction_time"] = pd.to_datetime(
        [fake.future_datetime(end_date="+10y") for _ in range(len(fut_idx))]
    )
    append_error(
        df,
        fut_idx,
        error_label="future transaction time",
        columns=["transaction_time"],
    )

    # Shipping discount > shipping fee
    over_sd = df[df["shipping_fee"] > 0].sample(frac=0.02, random_state=58).index
    df.loc[over_sd, "shipping_discount"] = [
        round(fee * random.uniform(1.1, 2.0), 2)
        for fee in df.loc[over_sd, "shipping_fee"]
    ]
    append_error(
        df,
        over_sd,
        error_label="shipping discount greater than shipping fee",
        columns=["shipping_fee", "shipping_discount"],
    )

    return save(df, "transactions_dirty.csv")


@register("dirty_transaction_items")
def dirty_transaction_items(ctx: GenerationContext):
    df = ctx.transactions.transaction_items_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # Orphaned items (transaction_id not in transactions)
    orphan_idx = df.sample(frac=0.02, random_state=60).index
    df.loc[orphan_idx, "transaction_id"] = [
        f"TRAN_{random.randint(1000, 9999)}" for _ in range(len(orphan_idx))
    ]
    append_error(
        df,
        orphan_idx,
        error_label="orphaned transaction item",
        columns=["transaction_id"],
    )

    # unit_price = 0
    unit_price_idx = df.sample(frac=0.02, random_state=61).index
    df.loc[unit_price_idx, "unit_price"] = 0.0
    append_error(
        df,
        unit_price_idx,
        error_label="zero unit price",
        columns=["unit_price"],
    )

    # quantity = 0 or negative
    qty_idx = df.sample(frac=0.02, random_state=62).index
    df.loc[qty_idx, "quantity"] = [
        random.choice([0, -abs(random.randint(1, 5))]) for _ in range(len(qty_idx))
    ]
    append_error(
        df,
        qty_idx,
        error_label="invalid quantity",
        columns=["quantity"],
    )

    # item_discount > item_subtotal
    disc_idx = df.sample(frac=0.02, random_state=63).index
    df.loc[disc_idx, "item_discount"] = [
        round(subtotal * random.uniform(1.1, 2.0), 2)
        for subtotal in df.loc[disc_idx, "item_subtotal"]
    ]
    append_error(
        df,
        disc_idx,
        error_label="item discount greater than item subtotal",
        columns=["item_discount", "item_subtotal"],
    )

    # final_item_price ≠ subtotal - discount
    math_idx = df.sample(frac=0.04, random_state=64).index
    df.loc[math_idx, "final_item_price"] = [
        round(price + random.uniform(-20, 20), 2)
        for price in df.loc[math_idx, "final_item_price"]
    ]
    append_error(
        df,
        math_idx,
        error_label="final item price mismatch",
        columns=["final_item_price", "item_subtotal", "item_discount"],
    )

    # Missing product_id
    df = inject_nulls(
        df,
        df["product_id"].isna(),
        "product_id",
        rate=0.02,
        error_label="missing product ID",
    )

    return save(df, "transaction_items_dirty.csv")
