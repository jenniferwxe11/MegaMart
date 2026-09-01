# dirty_data_generation/helpers/dirty_utils.py

import inspect
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()


# =============================================================================
# Row Sampling
# =============================================================================


def apply_corruption(
    df: pd.DataFrame,
    rate: float,
    corruption,
    ctx=None,
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
        if "ctx" in inspect.signature(corruption).parameters:
            corruption(
                df=df,
                idx=idx,
                ctx=ctx,
            )
        else:
            corruption(
                df=df,
                idx=idx,
            )


def generate_future_date():
    """
    Generate an intentionally invalid future date 1–10 years ahead.
    """

    today = datetime.today().date()

    return fake.date_between(
        start_date=today + timedelta(days=365),
        end_date=today + timedelta(days=365 * 10),
    )


def generate_future_datetime():
    """
    Generate an intentionally invalid future timestamp 1–10 years ahead.
    """

    now = datetime.now()

    return fake.date_time_between(
        start_date=now + timedelta(days=365),
        end_date=now + timedelta(days=365 * 10),
    )
