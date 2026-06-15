import random
from datetime import timedelta
from typing import Any

import pandas as pd

from data_generation.config.product_lifecycles_config import (
    PRODUCT_LIFECYCLE,
    STATUS_CHAIN,
    STATUS_DWELL_DAYS,
    STATUS_TRANSITION_PROB,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.utils.io_utils import save


@register("product_lifecycles_generator")
def product_lifecycles_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    product_ids = ctx.products.product_ids
    DATA_START_DATE = pd.Timestamp(ctx.config.DATA_START_DATE)
    DATA_END_DATE = pd.Timestamp(ctx.config.DATA_END_DATE)
    SIMULATION_DATE = pd.Timestamp(ctx.config.SIMULATION_DATE)

    # ---------------------------
    # Storage
    # ---------------------------

    product_lifecycles: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------
    for product_id in product_ids:

        # Skew launch dates towards earlier in the window so most products are mature
        launch_date = DATA_START_DATE + (DATA_END_DATE - DATA_START_DATE) * (
            random.random() ** 2
        )
        # Strip time component
        launch_date = launch_date.normalize()

        # Seed status: products launched very recently start as New
        if launch_date >= SIMULATION_DATE - timedelta(days=30):
            current_status = "New"
        else:
            current_status = random.choices(
                list(PRODUCT_LIFECYCLE.keys()),
                weights=list(PRODUCT_LIFECYCLE.values()),
                k=1,
            )[0]

        version_start = launch_date

        rows_for_product = []

        while True:
            dwell_min, dwell_max = STATUS_DWELL_DAYS.get(current_status, (60, 180))
            dwell_days = random.randint(dwell_min, dwell_max)
            version_end = version_start + timedelta(days=dwell_days)

            # Decide whether to transition to the next status at all
            candidates = STATUS_CHAIN.get(current_status, [])
            if not candidates:
                break

            next_status = random.choice(candidates)

            will_transition = (
                next_status is not None
                # Transition must happen within the data window
                and version_end <= DATA_END_DATE
                and random.random() < STATUS_TRANSITION_PROB.get(current_status, 0.0)
            )

            # If we ever hit Discontinued, lock discontinuation_date immediately
            row_discontinuation_date = (
                version_end if current_status == "Discontinued" else None
            )

            # --- Store Product Lifecycle Record ---
            rows_for_product.append(
                {
                    "product_id": product_id,
                    "status": current_status,
                    "launch_date": launch_date,
                    "discontinuation_date": row_discontinuation_date,
                    "valid_from": version_start,
                    "valid_to": version_end if will_transition else pd.NaT,
                    "is_current": not will_transition,
                }
            )

            if not will_transition:
                break

            current_status = next_status
            version_start = version_end

        product_lifecycles.extend(rows_for_product)

    # ---------------------------
    # Export
    # ---------------------------
    df = pd.DataFrame(product_lifecycles).sort_values(by=["product_id", "valid_from"])
    save(df, "product_lifecycles_raw.csv")
