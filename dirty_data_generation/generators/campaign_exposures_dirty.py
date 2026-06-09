import random
from datetime import timedelta

import pandas as pd

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import duplicate_rows
from dirty_data_generation.utils.io_utils import save


@register("dirty_campaign_exposures")
def dirty_campaign_exposures(ctx: GenerationContext):
    df = ctx.campaign_assignments.campaign_exposures_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    rows = []
    for _, row in df.iterrows():
        row = row.copy()

        # exposed = False but exposed_time is populated
        if (
            not row["exposed"]
            and random.random() < 0.03
            and pd.notna(row["exposed_time"])
        ):
            row["error_types"].append("exposed=False but exposed_time populated")
            pass  # keep the contradiction — that's the dirty data

        # clicked_time before opened_time
        if (
            pd.notna(row["clicked_time"])
            and pd.notna(row["opened_time"])
            and random.random() < 0.02
        ):
            row["clicked_time"], row["opened_time"] = (
                row["opened_time"],
                row["clicked_time"],
            )
            row["error_types"].append("clicked time before opened time")

        # opened_time before exposed_time
        if (
            pd.notna(row["opened_time"])
            and pd.notna(row["exposed_time"])
            and random.random() < 0.02
        ):
            row["opened_time"] = row["exposed_time"] - timedelta(
                minutes=random.randint(1, 60)
            )
            row["error_types"].append("opened time before exposed time")

        # Negative cost_per_msg
        if random.random() < 0.01 and pd.notna(row.get("cost_per_msg")):
            row["cost_per_msg"] = -abs(row.get("cost_per_msg", 0) or 0)
            row["error_types"].append("negative cost per message")

        # Missing channel
        if random.random() < 0.02 and pd.notna(row.get("channel")):
            row["channel"] = None
            row["error_types"].append("missing channel")

        rows.append(row)

    df_dirty = pd.DataFrame(rows)

    # Duplicate rows
    df_dirty = duplicate_rows(df_dirty, rate=0.03)

    return save(df_dirty, "campaign_exposures_dirty.csv")
