import random

from faker import Faker

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    duplicate_rows,
    inject_nulls,
    inject_whitespace,
)
from dirty_data_generation.utils.io_utils import save

fake = Faker()


@register("dirty_reviews")
def dirty_reviews(ctx: GenerationContext):
    df = ctx.product_reviews.product_reviews_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # Rating out of range
    oor_idx = df.sample(frac=0.03, random_state=80).index
    df.loc[oor_idx, "rating"] = [
        random.choice([0, -random.randint(1, 5), random.randint(6, 10)])
        for _ in range(len(oor_idx))
    ]
    append_error(df, oor_idx, "rating out of range")

    # Future review_date
    fut_idx = df.sample(frac=0.02, random_state=81).index
    df.loc[fut_idx, "review_date"] = [
        fake.future_datetime(end_date="+10y") for _ in range(len(fut_idx))
    ]
    append_error(df, fut_idx, "future review date")

    # Missing review_text
    df = inject_nulls(
        df,
        df["review_text"].isna(),
        "review_text",
        rate=0.04,
        error_label="missing review text",
    )

    # Duplicate reviews
    df = duplicate_rows(df, rate=0.04)

    # Rating/sentiment mismatch
    indices = df.sample(frac=0.02, random_state=2).index
    df.loc[indices, "rating"] = [random.randint(1, 5) for _ in range(len(indices))]
    append_error(df, indices, "rating/sentiment mismatch")

    # Whitespace in review_text
    df = inject_whitespace(
        df, col="review_text", rate=0.05, error_label="review text formatting anomaly"
    )

    return save(df, "product_reviews_dirty.csv")
