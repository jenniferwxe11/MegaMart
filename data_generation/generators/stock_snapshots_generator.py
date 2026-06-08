import random
from datetime import timedelta
from typing import Any

import pandas as pd

from data_generation.config.generation_config import LIMIT_STOCK_SNAPSHOTS
from data_generation.config.stocks_config import (
    BRAND_STOCKOUT_MULTIPLIER,
    CATEGORY_BASE_STOCK,
    CHANGE_REASONS,
    EVENT_STOCK_DROP_RATES,
    LIFECYCLE_STOCKOUT_MULTIPLIER,
    STOCK_BANDS,
    STOCK_STATUSES,
    STORE_OVERORDER_BIAS,
    STORE_STOCKOUT_MULTIPLIER,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.stocks.stock_snapshot_service import (
    date_range,
    get_seasonal_spike,
    get_stock_band,
)
from data_generation.utils.io_utils import save


@register("stock_snapshots_generator")
def stock_snapshots_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    DATA_START_DATE = pd.Timestamp(ctx.config.DATA_START_DATE)
    DATA_END_DATE = pd.Timestamp(ctx.config.DATA_END_DATE)

    stores_df = ctx.stores.stores_df
    products_df = ctx.products.products_df

    assert ctx.store_catalogues is not None
    store_catalogues_df = ctx.store_catalogues.store_catalogues_df

    assert ctx.product_lifecycles is not None
    product_lifecycles_df = ctx.product_lifecycles.product_lifecycles_df

    assert ctx.stockout_events is not None
    stockout_event_map = ctx.stockout_events.stockout_event_map

    # ---------------------------
    # Storage
    # ---------------------------

    # inventory_change_events: one row per meaningful stock movement
    inventory_change_events: list[dict[str, Any]] = []

    # weekly_snapshots: sparse — only emitted when stock_band or stock_status
    # actually changes relative to the previous week.
    weekly_snapshots: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    # Precompute seasonal demand windows
    seasonal_spikes = get_seasonal_spike()

    for _, row in store_catalogues_df.iterrows():

        if len(inventory_change_events) >= LIMIT_STOCK_SNAPSHOTS:
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

        launch_date = product_lifecycle_row.get("launch_date", DATA_START_DATE)
        discontinuation_date = product_lifecycle_row.get(
            "discontinuation_date", DATA_END_DATE
        )
        status = product_lifecycle_row.get("status", "Active")

        # --- Baseline inventory ---
        base_low, base_high = CATEGORY_BASE_STOCK.get(category, (20, 50))
        base_stock = random.randint(base_low, base_high)
        brand_mult = BRAND_STOCKOUT_MULTIPLIER.get(brand, 1.0)
        store_mult = STORE_STOCKOUT_MULTIPLIER.get(store_type, 1.0)
        store_variation = random.uniform(0.8, 1.2)
        lifecycle_status_mult = LIFECYCLE_STOCKOUT_MULTIPLIER.get(status, 1.0)
        base_stock = int(
            base_stock
            * brand_mult
            * store_mult
            * store_variation
            * lifecycle_status_mult
        )

        # Initialize weekly stock trajectory from baseline
        last_week_stock = base_stock
        # Used to gate sparse snapshot emission
        last_stock_band = None
        last_stock_status = None

        # Emit the opening balance as the first event
        inventory_change_events.append(
            {
                "store_id": store_id,
                "product_id": product_id,
                "timestamp": DATA_START_DATE,
                "delta": base_stock,
                "reason": "Opening balance",
                "stock_after": base_stock,
            }
        )

        # Identify stockout events impacting product
        product_stockouts = stockout_event_map.get(
            (store_id, product_id), pd.DataFrame()
        )

        for week_start_date in date_range(DATA_START_DATE, DATA_END_DATE):
            week_end_date = week_start_date + timedelta(days=6)

            # Filter out period outside product's active lifecycle
            if week_end_date < pd.Timestamp(
                launch_date
            ) or week_start_date > pd.Timestamp(discontinuation_date):
                continue

            # Ensure stock evolves over time to simulate continuity
            final_stock = last_week_stock
            reason_key = None

            # --- Seasonal demand windows ---
            for spike_start, spike_end, event_name in seasonal_spikes:
                if spike_start <= week_start_date <= spike_end:
                    if week_start_date <= spike_start + timedelta(weeks=1):
                        # Restock moderately before event
                        final_stock = int(final_stock * random.uniform(1.15, 1.5))
                        reason_key = "seasonal_restock"
                    else:
                        # Reduce stock after event
                        drop_min, drop_max = EVENT_STOCK_DROP_RATES.get(
                            event_name, (0.85, 0.95)
                        )
                        final_stock = int(
                            final_stock * random.uniform(drop_min, drop_max)
                        )
                        reason_key = "seasonal_drop"

            # --- Stockout windows ---
            if product_stockouts.empty:
                week_stockout = pd.DataFrame()
                next_week_stockout = pd.DataFrame()
            else:
                week_stockout = product_stockouts[
                    (product_stockouts["stockout_start_date"] <= week_end_date)
                    & (product_stockouts["stockout_end_date"] >= week_start_date)
                ]
                next_week_stockout = product_stockouts[
                    (
                        product_stockouts["stockout_start_date"]
                        <= week_end_date + timedelta(weeks=1)
                    )
                    & (product_stockouts["stockout_end_date"] >= week_end_date)
                ]

            if not week_stockout.empty:
                # If stockout occurs this week, drop inventory to zero
                final_stock = 0
                reason_key = "stockout"

            elif not next_week_stockout.empty:
                # If stockout is upcoming, proactively reduce stock
                final_stock = int(final_stock * random.uniform(0.05, 0.3))
                reason_key = "pre_stockout_drain"

            else:
                # --- Inventory management band logic ---
                over_stock = STOCK_BANDS["101+"][0]
                healthy_stock = STOCK_BANDS["21-100"][1]
                low_stock = STOCK_BANDS["6-20"][0]
                critical_stock = STOCK_BANDS["1-5"][0]

                # Overstocked: Reduce replenishment to avoid excess holding cost
                if final_stock > over_stock:
                    final_stock = int(final_stock * random.uniform(0.8, 0.95))
                    reason_key = "overstocked_reduction"

                # Healthy stock: Mostly stable, with occasional over-ordering (forecasting error)
                elif healthy_stock <= final_stock <= over_stock:
                    if random.random() < STORE_OVERORDER_BIAS.get(store_type, 0.1):
                        final_stock = int(final_stock * random.uniform(1.2, 1.6))
                        reason_key = "overorder"
                    else:
                        final_stock = int(final_stock * random.uniform(0.95, 1.1))
                        reason_key = "healthy_drift"

                # Low stock: Minor fluctuations, typical operational variance
                elif low_stock <= final_stock <= healthy_stock:
                    final_stock = int(final_stock * random.uniform(0.9, 1.1))
                    reason_key = "low_band_drift"

                # Critical stock: High likelihood of replenishment, but not guaranteed (operational delay)
                elif critical_stock <= final_stock < low_stock:
                    if random.random() < 0.2:
                        final_stock = int(final_stock * random.uniform(0.5, 0.8))
                        reason_key = "critical_decay"
                    else:
                        # Stock replenishment based on store
                        store_multiplier = STORE_STOCKOUT_MULTIPLIER.get(
                            store_type, 1.0
                        )
                        final_stock += int(
                            base_stock
                            * store_multiplier
                            * store_variation
                            * random.uniform(0.8, 1.2)
                        )
                        reason_key = "critical_replenish"

                # Extremely low stock: Immediate replenishment triggered
                elif final_stock < critical_stock:
                    # Stock replenishment based on store
                    store_multiplier = STORE_STOCKOUT_MULTIPLIER.get(store_type, 1.0)
                    final_stock += int(
                        base_stock
                        * store_multiplier
                        * store_variation
                        * random.uniform(1.0, 1.6)
                    )
                    reason_key = "critical_replenish"

                # End-of-life handling
                if discontinuation_date - week_end_date <= timedelta(weeks=2):
                    if random.random() < 0.9:
                        # Reduces replenishment probability significantly
                        final_stock = int(final_stock * random.uniform(0.5, 0.85))
                        reason_key = "eol_drawdown"
                    else:
                        # Small chance of replenishment
                        final_stock += int(base_stock * random.uniform(0.4, 0.8))
                        reason_key = "eol_final_restock"

                # Perishable spoilage
                if category in [
                    "Fresh Produce",
                    "Meat & Seafood",
                    "Bakery",
                    "Dairy & Eggs",
                ]:
                    if random.random() < 0.1:
                        # Random stock drops (spoilage/expiry losses)
                        final_stock = int(final_stock * random.uniform(0.05, 0.5))
                        reason_key = "spoilage"

                # Ensure stocks numbers are not negative
                final_stock = max(final_stock, 0)

            # --- Store Weekly Stock Record ---

            # Emit an inventory change event only if stock actually moved.
            delta = final_stock - last_week_stock
            if delta != 0 and reason_key is not None:
                inventory_change_events.append(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "timestamp": week_start_date,
                        "delta": delta,
                        "reason": CHANGE_REASONS[reason_key],
                        "stock_after": final_stock,
                    }
                )

            # Emit a sparse snapshot only when the stock BAND or STATUS changes.
            stock_band = get_stock_band(final_stock)
            stock_status = STOCK_STATUSES.get(stock_band, "")

            if stock_band != last_stock_band or stock_status != last_stock_status:
                weekly_snapshots.append(
                    {
                        "week_start_date": week_start_date,
                        "store_id": store_id,
                        "product_id": product_id,
                        "stock_status": stock_status,
                        "stock_band": stock_band,
                    }
                )
                last_stock_band = stock_band
                last_stock_status = stock_status

            last_week_stock = final_stock

    # ---------------------------
    # Export
    # ---------------------------

    df_events = pd.DataFrame(inventory_change_events).sort_values(
        by=["store_id", "product_id", "timestamp"]
    )
    df_snapshots = pd.DataFrame(weekly_snapshots).sort_values(
        by=["week_start_date", "store_id", "product_id"]
    )
    save(df_events, "inventory_change_events.csv")
    save(df_snapshots, "stock_snapshots_raw.csv")
