# dirty_data_generation/generators/bundles_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.bundle_items_rules import (
    bundle_item_category_mismatch,
    bundle_type_category_mismatch,
    bundle_type_quantity_mismatch,
    duplicate_product_within_bundle,
    invalid_bundle_item_quantity,
    missing_quantity,
)
from dirty_data_generation.corruption_rules.bundle_pricings_rules import (
    bundle_price_below_cost,
    bundle_price_out_of_range,
    bundle_price_progression_violation,
    bundle_pricing_lifecycle_gap,
    bundle_pricing_phase_out_of_order,
    discount_exceeds_bundle_price,
    discount_value_out_of_range,
    discount_value_progression_violation,
    duplicate_bundle_pricing_phase,
    end_date_before_start_date,
    invalid_bundle_pricing_lifecycle,
    missing_bundle_price,
    missing_discount_value,
    missing_pricing_phase,
)
from dirty_data_generation.corruption_rules.bundles_rules import (
    duplicate_category_inside_bundle,
    empty_bundle_categories,
    invalid_bundle_id_format,
    missing_bundle_name,
    missing_bundle_type,
    missing_categories,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

BUNDLE_RULES = [
    # Missing Values
    (0.03, missing_bundle_name),
    (0.03, missing_bundle_type),
    (0.03, missing_categories),
    # Formatting
    (0.02, invalid_bundle_id_format),
    # Business Rule Violations
    (0.02, duplicate_category_inside_bundle),
    (0.02, empty_bundle_categories),
]

BUNDLE_PRICINGS_RULES = [
    # Missing Values
    (0.03, missing_bundle_price),
    (0.03, missing_discount_value),
    (0.03, missing_pricing_phase),
    # Range Validation
    (0.02, bundle_price_out_of_range),
    (0.02, discount_value_out_of_range),
    # Business Rule Violations
    (0.02, end_date_before_start_date),
    (0.02, duplicate_bundle_pricing_phase),
    (0.02, discount_exceeds_bundle_price),
    (0.02, invalid_bundle_pricing_lifecycle),
    (0.02, bundle_pricing_phase_out_of_order),
    (0.02, bundle_pricing_lifecycle_gap),
    (0.02, bundle_price_progression_violation),
    (0.02, discount_value_progression_violation),
    (0.02, bundle_price_below_cost),
]


BUNDLE_ITEMS_RULES = [
    # Missing Values
    (0.03, missing_quantity),
    # Business Rule Violations
    (0.02, duplicate_product_within_bundle),
    (0.02, bundle_item_category_mismatch),
    (0.02, invalid_bundle_item_quantity),
    (0.02, bundle_type_quantity_mismatch),
    (0.02, bundle_type_category_mismatch),
]


@register("dirty_bundles")
def dirty_bundles(ctx: GenerationContext):

    df = ctx.bundles.bundles_df.copy()

    for rate, rule in BUNDLE_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "bundles_dirty.csv")


@register("dirty_bundle_pricings")
def dirty_bundle_pricings(ctx: GenerationContext):

    df = ctx.bundles.bundle_pricings_df.copy()

    for rate, rule in BUNDLE_PRICINGS_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "bundle_pricings_dirty.csv")


@register("dirty_bundle_items")
def dirty_bundle_items(ctx: GenerationContext):

    df = ctx.bundles.bundle_items_df.copy()

    for rate, rule in BUNDLE_ITEMS_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "bundle_items_dirty.csv")
