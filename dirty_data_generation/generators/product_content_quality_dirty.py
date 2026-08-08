# dirty_data_generation/generators/product_content_quality_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.product_content_quality_rules import (
    current_record_has_end_date,
    description_indicator_mismatch,
    description_length_out_of_bounds,
    duplicate_content_version_id,
    image_indicator_mismatch,
    image_quality_score_out_of_bounds,
    invalid_content_version_id_format,
    invalid_validity_period,
    missing_attribute_count,
    missing_attribute_count_out_of_bounds,
    missing_description_length,
    missing_has_description,
    missing_has_image,
    missing_image_count,
    missing_quality_tier,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

PRODUCT_CONTENT_QUALITY_RULES = [
    # Missing Values
    (0.03, missing_quality_tier),
    (0.03, missing_has_image),
    (0.03, missing_image_count),
    (0.03, missing_has_description),
    (0.03, missing_description_length),
    (0.03, missing_attribute_count),
    # Formatting
    (0.02, invalid_content_version_id_format),
    # Duplicates
    (0.02, duplicate_content_version_id),
    # Range Validation
    (0.02, image_quality_score_out_of_bounds),
    (0.02, description_length_out_of_bounds),
    (0.02, missing_attribute_count_out_of_bounds),
    # Business Rules
    (0.03, image_indicator_mismatch),
    (0.03, description_indicator_mismatch),
    (0.02, invalid_validity_period),
    (0.02, current_record_has_end_date),
]


@register("dirty_product_content_quality")
def dirty_product_content_quality(ctx: GenerationContext):

    df = ctx.product_content_quality.product_content_quality_df.copy()

    for rate, rule in PRODUCT_CONTENT_QUALITY_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "product_content_quality_dirty.csv")
