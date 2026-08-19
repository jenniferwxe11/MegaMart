from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.competitor_price_history_rules import (
    duplicate_competitor_scrape_record,
    future_update_timestamp,
    missing_competitor,
    missing_scraped_category,
    missing_scraped_price,
    missing_scraped_product_name,
    missing_update_timestamp,
    scraped_price_out_of_range,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

COMPETITOR_PRICE_HISTORY_RULES = [
    # Missing Values
    (0.03, missing_competitor),
    (0.03, missing_scraped_product_name),
    (0.03, missing_scraped_category),
    (0.03, missing_scraped_price),
    (0.03, missing_update_timestamp),
    # Range Validation
    (0.02, scraped_price_out_of_range),
    # Business Rule Violations
    (0.03, future_update_timestamp),
    (0.03, duplicate_competitor_scrape_record),
]


@register("dirty_competitor_price_history")
def dirty_competitor_price_history(ctx: GenerationContext):

    df = ctx.competitor_products.competitor_price_history_df.copy()

    for rate, rule in COMPETITOR_PRICE_HISTORY_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "competitor_price_history_dirty.csv")
