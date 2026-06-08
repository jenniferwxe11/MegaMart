import random
from datetime import date, timedelta
from typing import Any

import pandas as pd
from faker import Faker

from data_generation.config.generation_config import LIMIT_STOCKOUT_EVENTS
from data_generation.config.stocks_config import (
    BRAND_STOCKOUT_MULTIPLIER,
    BRAND_STOCKOUT_NUM_OF_TIMES_MULTIPLIER,
    CATEGORY_STOCKOUT_PROB,
    LIFECYCLE_STOCKOUT_MULTIPLIER,
    STOCKOUT_AMOUNT_OF_TIMES_BY_CATEGORY,
    STOCKOUT_DURATION_BY_CATEGORY,
    STOCKOUT_DURATION_BY_STATUS,
    STORE_STOCKOUT_MULTIPLIER,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.utils.date_time_utils import overlapping_dates
from data_generation.utils.io_utils import save

fake = Faker()


@register("stockout_events_generator")
def stockout_events_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    DATA_START_DATE = ctx.config.DATA_START_DATE
    DATA_END_DATE = ctx.config.DATA_END_DATE
    stores_df = ctx.stores.stores_df
    products_df = ctx.products.products_df

    assert ctx.store_catalogues is not None
    store_catalogues_df = ctx.store_catalogues.store_catalogues_df

    assert ctx.product_lifecycles is not None
    product_lifecycles_df = ctx.product_lifecycles.product_lifecycles_df

    # ---------------------------
    # Storage
    # ---------------------------

    stockout_events: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    for _, row in store_catalogues_df.iterrows():

        if len(stockout_events) >= LIMIT_STOCKOUT_EVENTS:
            break

        store_id = row["store_id"]
        product_id = row["product_id"]
        product_match = products_df.loc[products_df["product_id"] == product_id]

        if product_match.empty:
            continue

        product_row = product_match.iloc[0]

        store_match = stores_df.loc[stores_df["store_id"] == store_id]
        if store_match.empty:
            continue
        store_row = store_match.iloc[0]

        brand = product_row["brand"]
        category = product_row["category"]
        store_type = store_row["store_type"]

        product_lifecycle_match = product_lifecycles_df.loc[
            product_lifecycles_df["product_id"] == product_id
        ]
        if product_lifecycle_match.empty:
            continue
        product_lifecycle_row = product_lifecycle_match.iloc[0]

        launch_date = product_lifecycle_row.get(
            "launch_date", pd.Timestamp(DATA_START_DATE)
        )
        discontinuation_date = product_lifecycle_row.get(
            "discontinuation_date", pd.Timestamp(DATA_END_DATE)
        )
        status = product_lifecycle_row.get("status", "Active")

        # --------------------------------------------------------
        # Determine likelihood of stockout based on:
        # - Category supply sensitivity
        # - Brand reliability
        # - Store type, operations
        # - Product lifecycle stage
        # --------------------------------------------------------

        category_prob = CATEGORY_STOCKOUT_PROB.get(category, 0.05)
        brand_mult = BRAND_STOCKOUT_MULTIPLIER.get(brand, 1.0)
        store_mult = STORE_STOCKOUT_MULTIPLIER.get(store_type, 1.0)
        store_variation = random.uniform(0.8, 1.2)
        lifecycle_status_mult = LIFECYCLE_STOCKOUT_MULTIPLIER.get(status, 1.0)

        if random.random() > min(
            category_prob
            * brand_mult
            * store_mult
            * store_variation
            * lifecycle_status_mult,
            1.0,
        ):
            continue

        for year in range(DATA_START_DATE.year, DATA_END_DATE.year + 1):
            # Filter out period outside product's active lifecycle
            if launch_date.year > year:
                continue
            if pd.notna(discontinuation_date) and discontinuation_date.year < year:
                continue

            # Determine number of stockout events per year
            is_year_of_discontinuation = (
                pd.notna(discontinuation_date) and discontinuation_date.year == year
            )
            base_min, base_max = STOCKOUT_AMOUNT_OF_TIMES_BY_CATEGORY.get(
                category, (1, 2)
            )
            base_events = random.randint(base_min, base_max)
            intensity = (
                BRAND_STOCKOUT_NUM_OF_TIMES_MULTIPLIER.get(brand, 1.0)
                * store_mult
                * store_variation
                * lifecycle_status_mult
                # Increase stockout frequency during discontinuation phase
                * 1.8
                if is_year_of_discontinuation
                else 1.0
            )
            num_yearly_stockouts = int(base_events * intensity)
            num_yearly_stockouts = max(1, min(num_yearly_stockouts, 30))

            existing_stockout_windows: list[tuple[pd.Timestamp, pd.Timestamp]] = []

            # Generate multiple non overlapping stockout windows
            for _ in range(num_yearly_stockouts):

                if status == "Discontinued":
                    stockout_start_date = discontinuation_date
                    stockout_end_date = None
                else:
                    # Stockout duration determined by product lifecycle status and category
                    status_min, status_max = STOCKOUT_DURATION_BY_STATUS[status]
                    cat_min, cat_max = STOCKOUT_DURATION_BY_CATEGORY[category]
                    min_duration = max(status_min, cat_min)
                    max_duration = min(status_max, cat_max)
                    if min_duration <= max_duration:
                        stockout_duration_days = random.randint(
                            min_duration,
                            max_duration * (2 if is_year_of_discontinuation else 1),
                        )
                    else:
                        stockout_duration_days = random.randint(
                            max_duration,
                            min_duration * (2 if is_year_of_discontinuation else 1),
                        )

                    # Prevent unrealistic clustering of stockout windows
                    for _ in range(10):
                        stockout_start_date = fake.date_between(
                            start_date=max(launch_date, pd.Timestamp(date(year, 1, 1))),
                            end_date=date(year, 12, 31),
                        )
                        stockout_end_date = stockout_start_date + timedelta(
                            days=stockout_duration_days
                        )

                        if not overlapping_dates(
                            existing_stockout_windows,
                            stockout_start_date,
                            stockout_end_date,
                        ):
                            existing_stockout_windows.append(
                                (stockout_start_date, stockout_end_date)
                            )

                            # Store Stockout Record
                            stockout_events.append(
                                {
                                    "store_id": store_id,
                                    "product_id": product_id,
                                    "stockout_start_date": stockout_start_date,
                                    "stockout_end_date": stockout_end_date,
                                }
                            )
                            break

    # ---------------------------
    # Export to CSV
    # ---------------------------

    df_stockout_events = pd.DataFrame(stockout_events)
    df_stockout_events = df_stockout_events.sort_values(
        by=["store_id", "product_id", "stockout_start_date"]
    )
    save(df_stockout_events, "stockout_events_raw.csv")
