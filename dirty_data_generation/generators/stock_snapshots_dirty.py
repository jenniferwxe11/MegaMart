# dirty_data_generation/generators/stock_snapshots_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.stock_snapshots_rules import (
    duplicate_stock_snapshot,
    future_week_start_date,
    invalid_stock_band,
    invalid_stock_band_status_combination,
    invalid_stock_status,
    missing_product_id,
    missing_stock_band,
    missing_stock_status,
    missing_store_id,
    missing_week_start_date,
    no_consecutive_duplicate_status,
    snapshot_outside_product_lifecycle,
    store_product_snapshot_mismatch,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

STOCK_SNAPSHOT_RULES = [
    # Missing Values
    (0.03, missing_week_start_date),
    (0.03, missing_store_id),
    (0.03, missing_product_id),
    (0.03, missing_stock_status),
    (0.03, missing_stock_band),
    # Accepted Values
    (0.02, invalid_stock_status),
    (0.02, invalid_stock_band),
    # Business Rule Violations
    (0.02, future_week_start_date),
    (0.03, duplicate_stock_snapshot),
    (0.03, snapshot_outside_product_lifecycle),
    (0.03, no_consecutive_duplicate_status),
    (0.03, invalid_stock_band_status_combination),
    # Cross-Entity Consistency
    (0.02, store_product_snapshot_mismatch),
]


@register("dirty_stock_snapshots")
def dirty_stock_snapshots(ctx: GenerationContext):

    df = ctx.stock_snapshots.stock_snapshots_df.copy()

    for rate, rule in STOCK_SNAPSHOT_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "stock_snapshots_dirty.csv")
