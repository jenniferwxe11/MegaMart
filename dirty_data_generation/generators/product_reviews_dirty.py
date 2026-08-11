# dirty_data_generation/generators/product_reviews_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.product_reviews_rules import (
    duplicate_review_id,
    duplicate_transaction_product_pair,
    future_review_date,
    invalid_review_id_format,
    missing_rating,
    missing_review_date,
    rating_out_of_bounds,
    review_before_transaction,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

PRODUCT_REVIEW_RULES = [
    # Missing Values
    (0.03, missing_review_date),
    (0.03, missing_rating),
    # Formatting
    (0.02, invalid_review_id_format),
    # Duplicates
    (0.02, duplicate_review_id),
    # Range Validation
    (0.03, rating_out_of_bounds),
    # Business Rules
    (0.02, future_review_date),
    (0.02, review_before_transaction),
    (0.02, duplicate_transaction_product_pair),
]


@register("dirty_product_reviews")
def dirty_product_reviews(ctx: GenerationContext):

    df = ctx.product_reviews.product_reviews_df.copy()

    for rate, rule in PRODUCT_REVIEW_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "product_reviews_dirty.csv")
