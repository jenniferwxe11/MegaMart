# dirty_data_generation/generators/store_catalogues_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.store_catalogues_rules import (
    blank_store_product_name,
    duplicate_store_product,
    missing_product_id,
    missing_store_brand,
    missing_store_category,
    missing_store_id,
    missing_store_product_name,
    missing_store_selling_price,
    store_price_product_price_mismatch,
    store_selling_price_out_of_range,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

STORE_CATALOGUE_RULES = [
    # Missing Values
    (0.03, missing_store_id),
    (0.03, missing_product_id),
    (0.03, missing_store_product_name),
    (0.03, blank_store_product_name),
    (0.03, missing_store_brand),
    (0.03, missing_store_category),
    (0.03, missing_store_selling_price),
    # Range Validation
    (0.02, store_selling_price_out_of_range),
    # Business Rule Violations
    (0.03, duplicate_store_product),
    (0.03, store_price_product_price_mismatch),
]


@register("dirty_store_catalogues")
def dirty_store_catalogues(ctx: GenerationContext):

    df = ctx.store_catalogues.store_catalogues_df.copy()

    for rate, rule in STORE_CATALOGUE_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "store_catalogues_dirty.csv")
