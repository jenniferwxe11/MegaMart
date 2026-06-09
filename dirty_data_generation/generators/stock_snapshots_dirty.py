import random

from faker import Faker

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    MAX_ERRORS_PER_ROW,
    duplicate_rows,
)
from dirty_data_generation.utils.io_utils import save

fake = Faker()


@register("dirty_stock_snapshots")
def dirty_stock_snapshots(ctx: GenerationContext):
    df = ctx.stock_snapshots.stock_snapshots_df.copy()
    df["error_types"] = [[] for _ in range(len(df))]

    # Sort so we can detect transitions per (store_id, product_id)
    df = df.sort_values(["store_id", "product_id", "week_start_date"]).reset_index(
        drop=True
    )

    for i, _ in df.iterrows():
        n_errors = len(set(df.at[i, "error_types"]))
        if n_errors >= MAX_ERRORS_PER_ROW:
            continue

        # Invalid stock status value
        if (
            random.random() < 0.03
            and "invalid stock status value" not in df.at[i, "error_types"]
        ):
            df.at[i, "stock_status"] = random.choice(
                ["STOCKED", "unavailable", "tbc", "999", "no stock", "0"]
            )
            df.at[i, "error_types"].append("invalid stock status value")
            n_errors += 1

        # Future week_start_date
        if (
            random.random() < 0.02
            and n_errors < MAX_ERRORS_PER_ROW
            and "future week start date" not in df.at[i, "error_types"]
        ):
            df.at[i, "week_start_date"] = fake.future_datetime(end_date="+10y")

            df.at[i, "error_types"].append("future week start date")
            n_errors += 1

        # Missing snapshot — null out stock fields to simulate a dropped week
        if (
            random.random() < 0.02
            and n_errors < MAX_ERRORS_PER_ROW
            and "missing snapshot data" not in df.at[i, "error_types"]
        ):
            df.at[i, "stock_level"] = None
            df.at[i, "error_types"].append("missing snapshot data")

    # Duplicate rows
    df = duplicate_rows(df, rate=0.01, error_label="duplicate row")

    return save(df, "stock_snapshots_dirty.csv")
