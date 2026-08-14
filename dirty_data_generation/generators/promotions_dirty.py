# dirty_data_generation/generators/promotions_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.promotions_rules import (
    discontinued_product_promotion_overlap,
    duplicate_promotion_id,
    free_shipping_invalid_scope,
    invalid_discount_code_format,
    invalid_effective_period,
    invalid_promotion_id_format,
    invalid_promotion_mechanic,
    invalid_promotion_scope,
    min_spend_out_of_range,
    missing_discount_code,
    missing_effective_end_date,
    missing_effective_start_date,
    missing_promotion_name,
    missing_promotion_target_id,
    missing_promotion_theme,
    missing_promotion_value,
    priority_out_of_range,
    promotion_value_out_of_range,
    zero_value_non_free_shipping,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

PROMOTION_RULES = [
    # Missing Values
    (0.03, missing_promotion_name),
    (0.03, missing_promotion_theme),
    (0.03, missing_promotion_target_id),
    (0.03, missing_promotion_value),
    (0.03, missing_discount_code),
    (0.03, missing_effective_start_date),
    (0.03, missing_effective_end_date),
    # Accepted Values
    (0.02, invalid_promotion_mechanic),
    (0.02, invalid_promotion_scope),
    # Formatting
    (0.02, invalid_promotion_id_format),
    (0.03, invalid_discount_code_format),
    # Duplicates
    (0.02, duplicate_promotion_id),
    # Range Validation
    (0.02, promotion_value_out_of_range),
    (0.02, min_spend_out_of_range),
    (0.02, priority_out_of_range),
    # Business Rule Violations
    (0.03, invalid_effective_period),
    (0.03, zero_value_non_free_shipping),
    (0.03, free_shipping_invalid_scope),
    (0.03, discontinued_product_promotion_overlap),
]


@register("dirty_promotions")
def dirty_promotions(ctx: GenerationContext):

    df = ctx.promotions.promotions_df.copy()

    for rate, rule in PROMOTION_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "promotions_dirty.csv")
