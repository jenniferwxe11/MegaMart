# dirty_data_generation/helpers/dirty_utils.py

import random

import pandas as pd

# =============================================================================
# Row Sampling
# =============================================================================


def apply_corruption(
    df: pd.DataFrame,
    rate: float,
    corruption,
    ctx,
    mask: pd.Series | None = None,
):

    if mask is None:
        mask = pd.Series(True, index=df.index)

    eligible = list(df.index[mask])

    if not eligible:
        return

    n = max(1, int(len(eligible) * rate))

    chosen = random.sample(
        eligible,
        min(n, len(eligible)),
    )

    for idx in chosen:
        corruption(
            df=df,
            idx=idx,
            ctx=ctx,
        )
