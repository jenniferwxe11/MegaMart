from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.inventory_change_events_rules import (
    delta_matches_stock_after_movement,
    duplicate_inventory_change_event,
    future_event_timestamp,
    invalid_reason,
    missing_event_timestamp,
    missing_product_id,
    missing_store_id,
    opening_balance_delta_matches_stock_after,
    opening_balance_first_record,
    opening_balance_uniqueness,
    stock_after_out_of_range,
    zero_delta,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

INVENTORY_CHANGE_EVENT_RULES = [
    # Missing Values
    (0.03, missing_store_id),
    (0.03, missing_product_id),
    (0.03, missing_event_timestamp),
    # Accepted Values
    (0.02, invalid_reason),
    # Range Validation
    (0.02, stock_after_out_of_range),
    # Business Rule Violations
    (0.02, future_event_timestamp),
    (0.03, duplicate_inventory_change_event),
    (0.03, delta_matches_stock_after_movement),
    (0.03, zero_delta),
    # Opening Balance Rules
    (0.02, opening_balance_first_record),
    (0.02, opening_balance_uniqueness),
    (0.03, opening_balance_delta_matches_stock_after),
]


@register("dirty_inventory_change_events")
def dirty_inventory_change_events(ctx: GenerationContext):

    df = ctx.stock_snapshots.inventory_change_events_df.copy()

    for rate, rule in INVENTORY_CHANGE_EVENT_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(
        df,
        "inventory_change_events_dirty.csv",
    )
