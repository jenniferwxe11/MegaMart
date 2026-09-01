# dirty_data_generation/generators/products_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.products_rules import (
    cost_price_greater_than_selling_price,
    cost_price_out_of_range,
    duplicate_product_id,
    invalid_product_id_format,
    invalid_product_name_format,
    missing_brand,
    missing_category,
    missing_cost_price,
    missing_product_name,
    missing_selling_price,
    selling_price_out_of_range,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

PRODUCT_RULES = [
    # Missing Values
    (0.04, missing_product_name),
    (0.04, missing_brand),
    (0.03, missing_category),
    (0.03, missing_selling_price),
    (0.03, missing_cost_price),
    # Formatting
    (0.03, invalid_product_id_format),
    (0.03, invalid_product_name_format),
    # Duplicates
    (0.03, duplicate_product_id),
    # Range Validation
    (0.03, selling_price_out_of_range),
    (0.03, cost_price_out_of_range),
    # Business Rule Violations
    (0.03, cost_price_greater_than_selling_price),
]


@register("dirty_products")
def dirty_products(ctx: GenerationContext):

    df = ctx.products.products_df.copy()

    for rate, rule in PRODUCT_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "products_dirty.csv")
