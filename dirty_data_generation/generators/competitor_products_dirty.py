import random

import pandas as pd
from faker import Faker

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    duplicate_rows,
    inject_nulls,
)
from dirty_data_generation.utils.io_utils import save

fake = Faker()


@register("dirty_competitor_products")
def dirty_competitor_products(ctx: GenerationContext):
    df = ctx.competitor_products.competitor_price_history_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # Price = 0 or negative
    zero_idx = (
        df[df["scraped_price"].notna() & df["scraped_price"] < 0]
        .sample(frac=0.02, random_state=90)
        .index
    )
    df.loc[zero_idx, "scraped_price"] = [
        random.choice([0, -abs(random.uniform(1, 50))]) for _ in range(len(zero_idx))
    ]
    append_error(df, zero_idx, "zero or negative scraped price")

    # Price spike >5×
    spike_idx = df.sample(frac=0.02, random_state=91).index
    df.loc[spike_idx, "scraped_price"] = (
        df.loc[spike_idx, "scraped_price"] * random.uniform(5.0, 10.0)
    ).round(2)
    append_error(df, spike_idx, "price spike greater than 5x")

    # Future update_timestamp
    fut_idx = df.sample(frac=0.02, random_state=92).index
    df.loc[fut_idx, "update_timestamp"] = [
        fake.future_datetime(end_date="+10y") for _ in range(len(fut_idx))
    ]
    append_error(df, fut_idx, "future update timestamp")

    # Duplicate rows
    df = duplicate_rows(df, rate=0.04)

    # Missing scraped_category
    df = inject_nulls(
        df,
        df["scraped_category"].isna(),
        "scraped_category",
        rate=0.03,
        error_label="missing scraped category",
    )

    # has_active_promo stored as "True"/"False" string
    df = df.astype({"has_active_promo": "object"})
    str_mask = pd.Series(
        [random.random() < 0.05 for _ in range(len(df))], index=df.index
    )
    df.loc[str_mask, "has_active_promo"] = df.loc[str_mask, "has_active_promo"].map(
        {True: "True", False: "False"}
    )
    append_error(df, str_mask[str_mask].index, "has_active_promo stored as string")

    return save(df, "competitor_price_history_dirty.csv")
