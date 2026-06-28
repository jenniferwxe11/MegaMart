import pandas as pd

from data_generation.config.clickstreams_config import (
    IN_STOCK_STATUS,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_product_stock_status,
    get_random_in_stock_product_from_category,
)
from tests.helpers import (
    _build_datetime,
)

# ============================================================
# get_product_stock_status()
# ============================================================
# Integration contract: uses stock snapshots data


def test_inventory_product_flow_get_product_stock_status_gets_latest_status(
    ctx,
):
    df = ctx.stock_snapshots.stock_snapshots_df
    row = df.iloc[0]
    store_id = row["store_id"]
    product_id = row["product_id"]
    matching_rows = df[(df["store_id"] == store_id) & (df["product_id"] == product_id)]
    timestamp = matching_rows["week_start_date"].max()
    expected = (
        matching_rows[matching_rows["week_start_date"] <= timestamp]
        .sort_values("week_start_date", ascending=False)
        .iloc[0]["stock_status"]
    )
    result = get_product_stock_status(
        ctx,
        store_id,
        product_id,
        timestamp,
    )
    assert result == expected


def test_inventory_product_flow_get_product_stock_status_no_matching_snapshot(
    ctx,
):
    # Pick IDs that do not exist in dataset
    store_id = "NON_EXISTENT_STORE"
    product_id = "NON_EXISTENT_PRODUCT"
    timestamp = _build_datetime()

    result = get_product_stock_status(
        ctx,
        store_id,
        product_id,
        timestamp,
    )

    assert result == "Out of Stock"


def test_inventory_product_flow_get_product_stock_status_before_first_snapshot(
    ctx,
):
    df = ctx.stock_snapshots.stock_snapshots_df
    row = df.iloc[0]
    store_id = row["store_id"]
    product_id = row["product_id"]
    matching_rows = df[(df["store_id"] == store_id) & (df["product_id"] == product_id)]

    # Choose a timestamp before all snapshots
    timestamp = matching_rows["week_start_date"].min() - pd.Timedelta(days=1)

    result = get_product_stock_status(
        ctx,
        store_id,
        product_id,
        timestamp,
    )

    assert result == "Out of Stock"


# ============================================================
# get_random_in_stock_product_from_category()
# ============================================================
# Integration contract: uses stock snapshots + product catalogue data


def test_inventory_product_flow_get_random_in_stock_product_from_category(
    ctx,
):
    df = ctx.stock_snapshots.stock_snapshots_df
    row = df.iloc[0]
    store_id = row["store_id"]
    product_id = row["product_id"]
    timestamp = row["week_start_date"]
    category = ctx.products.products_df[
        ctx.products.products_df["product_id"] == product_id
    ].iloc[0]["category"]
    result = get_random_in_stock_product_from_category(
        ctx, category, store_id, timestamp
    )

    if result is None:
        # Verify no in stock products exist
        product_ids = ctx.products.category_to_products[category]

        assert all(
            get_product_stock_status(ctx, store_id, pid, timestamp)
            not in IN_STOCK_STATUS
            for pid in product_ids
        )
    else:
        assert result in ctx.products.category_to_products[category]
        assert (
            get_product_stock_status(ctx, store_id, result, timestamp)
            in IN_STOCK_STATUS
        )
