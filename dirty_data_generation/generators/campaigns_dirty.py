import random

import pandas as pd

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    inject_nulls,
    inject_whitespace,
)
from dirty_data_generation.utils.io_utils import save


@register("dirty_campaigns")
def dirty_campaigns(ctx: GenerationContext):
    df = ctx.campaigns.campaigns_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # Negative budget
    neg_idx = df.sample(frac=0.02, random_state=30).index
    df.loc[neg_idx, "budget"] = -abs(df.loc[neg_idx, "budget"])
    append_error(df, neg_idx, "negative budget")

    # Astronomical budget
    big_idx = df.sample(frac=0.01, random_state=31).index
    df.loc[big_idx, "budget"] = [
        random.randint(10_000_000, 5_000_000_000) for _ in range(len(big_idx))
    ]
    append_error(df, big_idx, "astronomical budget")

    # end_date < start_date
    inv_idx = df.sample(frac=0.02, random_state=32).index
    df.loc[inv_idx, ["start_date", "end_date"]] = df.loc[
        inv_idx, ["end_date", "start_date"]
    ].values
    append_error(df, inv_idx, "inverted date range")

    # Missing target_segment
    df = inject_nulls(
        df,
        df["target_segment"].isna(),
        "target_segment",
        rate=0.03,
        error_label="missing target segment",
    )

    # is_ab_test stored as "True"/"False" string
    df = df.astype({"is_ab_test": "object"})
    str_mask = pd.Series(
        [random.random() < 0.05 for _ in range(len(df))], index=df.index
    )
    df.loc[str_mask, "is_ab_test"] = df.loc[str_mask, "is_ab_test"].map(
        {True: "True", False: "False"}
    )
    append_error(df, str_mask[str_mask].index, "is_ab_test stored as string")

    # Whitespace in campaign_name
    df = inject_whitespace(
        df,
        col="campaign_name",
        rate=0.04,
        error_label="campaign name formatting anomaly",
    )

    return save(df, "campaigns_dirty.csv")
