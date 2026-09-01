import random
from typing import Any

import pandas as pd
from faker import Faker

from data_generation.config.constants import DATA_END_DATE
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
from data_generation.utils.io_utils import save

fake = Faker()


@register("stockout_events_generator")
def stockout_events_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

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

        category_prob = CATEGORY_STOCKOUT_PROB.get(category, 0.05)
        brand_mult = BRAND_STOCKOUT_MULTIPLIER.get(brand, 1.0)
        store_mult = STORE_STOCKOUT_MULTIPLIER.get(store_type, 1.0)
        store_variation = random.uniform(0.8, 1.2)

        product_lifecycle_rows = product_lifecycles_df.loc[
            product_lifecycles_df["product_id"] == product_id
        ]

        if product_lifecycle_rows.empty:
            continue

        for _, lifecycle_row in product_lifecycle_rows.iterrows():

            status = lifecycle_row["status"]
            is_discontinued = status == "Discontinued"
            lifecycle_status_mult = LIFECYCLE_STOCKOUT_MULTIPLIER.get(status, 1.0)

            # --------------------------------------------------------
            # Determine likelihood of stockout based on:
            # - Category supply sensitivity
            # - Brand reliability
            # - Store type, operations
            # - Product lifecycle stage
            # --------------------------------------------------------

            prob = min(
                category_prob
                * brand_mult
                * store_mult
                * store_variation
                * lifecycle_status_mult,
                1.0,
            )

            if random.random() > prob:
                continue

            valid_from = lifecycle_row["valid_from"]

            valid_to = (
                lifecycle_row["valid_to"]
                if pd.notna(lifecycle_row["valid_to"])
                else pd.Timestamp(DATA_END_DATE)
            )

            discontinuation_date = lifecycle_row["discontinuation_date"]

            base_min, base_max = STOCKOUT_AMOUNT_OF_TIMES_BY_CATEGORY.get(
                category, (1, 2)
            )
            base_events = random.randint(base_min, base_max)
            intensity = (
                BRAND_STOCKOUT_NUM_OF_TIMES_MULTIPLIER.get(brand, 1.0)
                * store_mult
                * lifecycle_status_mult
            )

            num_phase_stockouts = int(base_events * intensity)
            num_phase_stockouts = max(1, min(num_phase_stockouts, 30))

            last_end = None

            if is_discontinued:
                stockout_events.append(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "stockout_start_date": discontinuation_date,
                        "stockout_end_date": None,
                    }
                )

                continue

            # Generate multiple non overlapping stockout windows
            for _ in range(num_phase_stockouts):

                # Stockout duration determined by product lifecycle status and category
                status_min, status_max = STOCKOUT_DURATION_BY_STATUS[status]
                cat_min, cat_max = STOCKOUT_DURATION_BY_CATEGORY[category]
                min_duration = max(status_min, cat_min)
                max_duration = min(status_max, cat_max)
                if min_duration <= max_duration:
                    stockout_duration_days = random.randint(
                        min_duration,
                        max_duration * (2 if status == "Phasing Out" else 1),
                    )
                else:
                    stockout_duration_days = random.randint(
                        max_duration,
                        min_duration * (2 if status == "Phasing Out" else 1),
                    )

                # Lower bound: respect both lifecycle start and previous window end
                min_start = valid_from

                if last_end is not None:
                    min_start = max(min_start, last_end + pd.Timedelta(days=1))

                # Upper bound: end of lifecycle phase
                max_start = valid_to

                # No room left in this lifecycle phase
                if min_start > max_start:
                    break

                # Ensure there's room for at least the minimum duration
                latest_viable_start = max_start - pd.Timedelta(days=min_duration)
                if min_start > latest_viable_start:
                    break

                stockout_start_date = pd.Timestamp(
                    fake.date_between(
                        start_date=min_start.date(),
                        end_date=latest_viable_start.date(),
                    )
                )
                stockout_end_date = min(
                    stockout_start_date + pd.Timedelta(days=stockout_duration_days),
                    valid_to,
                )
                last_end = stockout_end_date

                # Store Stockout Record
                stockout_events.append(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "stockout_start_date": stockout_start_date,
                        "stockout_end_date": stockout_end_date,
                    }
                )

    # ---------------------------
    # Export to CSV
    # ---------------------------

    df_stockout_events = pd.DataFrame(stockout_events)
    df_stockout_events = df_stockout_events.sort_values(
        by=["store_id", "product_id", "stockout_start_date"]
    )
    save(df_stockout_events, "stockout_events_raw.csv")
