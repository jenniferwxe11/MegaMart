import random
from datetime import timedelta

import pandas as pd
from faker import Faker

from data_generation.config.constants import DATA_END_DATE, DATA_START_DATE

fake = Faker()


def bundle_lifecycle(
    ctx,
    selected_products,
):
    """
    Determines valid bundle lifecycle window based on
    overlapping product availability.
    """
    product_launch_map = ctx.product_lifecycles.product_launch_map
    product_discontinuation_map = ctx.product_lifecycles.product_discontinuation_map

    launch_dates = []
    discontinuation_dates = []

    # ---------------------------------------------------------
    # Collect lifecycle dates
    # ---------------------------------------------------------

    for product_id, _ in selected_products:
        launch = product_launch_map.get(product_id, None)
        if not pd.isna(launch):
            launch_dates.append(launch)

        discontinuation = product_discontinuation_map.get(product_id, None)
        if not pd.isna(discontinuation):
            discontinuation_dates.append(discontinuation)

    # ---------------------------------------------------------
    # Determine overlap window
    # ---------------------------------------------------------
    launch_date = max(launch_dates) if launch_dates else None

    discontinuation_date = min(discontinuation_dates) if discontinuation_dates else None

    # No valid overlap
    if launch_date and discontinuation_date and launch_date > discontinuation_date:
        return None, None

    # Fallback defaults
    if launch_date is None:
        launch_date = pd.Timestamp(DATA_START_DATE)

    if discontinuation_date is None:
        discontinuation_date = pd.Timestamp(DATA_END_DATE)

    # ---------------------------------------------------------
    # Generate promotion window (30–120 days)
    # ---------------------------------------------------------

    effective_start_date = fake.date_time_between(
        start_date=launch_date, end_date=discontinuation_date
    )
    effective_end_date = min(
        pd.Timestamp(effective_start_date + timedelta(days=random.randint(30, 120))),
        pd.Timestamp(discontinuation_date),
        pd.Timestamp(DATA_END_DATE),
    )

    return effective_start_date, effective_end_date
