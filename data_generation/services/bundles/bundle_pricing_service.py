import random
from datetime import timedelta

import pandas as pd

from data_generation.config.bundles_config import (
    MAX_DISCOUNT_PCT,
    MIN_PHASE_DAYS,
    MIN_WINDOW_FOR_SPLIT,
    PHASE_STEP,
)


def calculate_bundle_pricing(
    ctx,
    bundle_type,
    selected_products,
):
    """
    Calculates bundle price and discount based on bundle type and product composition.
    Constraint: Maintain positive margin (price ≥ total cost)
    """
    product_price_map = ctx.products.product_price_map
    product_cost_map = ctx.products.product_cost_map

    total_price = 0
    total_cost = 0

    for product_id, quantity in selected_products:
        price = product_price_map.get(product_id, 0.0)
        cost = product_cost_map.get(product_id, 0.0)
        total_price += price * quantity
        total_cost += cost * quantity

    # ---------------------------------------------------------
    # Buy One Get One
    # ---------------------------------------------------------

    if bundle_type == "Buy One, Get One":
        bundle_price = max(total_price / 2, total_cost)
        discount_value = round(total_price - bundle_price, 2)

    # ---------------------------------------------------------
    # Set Bundles
    # ---------------------------------------------------------

    elif bundle_type == "Set":
        # Apply controlled discount (10–20%) to preserve margin
        discount_multiplier = random.uniform(0.85, 0.95)
        bundle_price = max(total_price * discount_multiplier, total_cost)
        discount_value = round(total_price - bundle_price, 2)

    # ---------------------------------------------------------
    # 2 For X
    # ---------------------------------------------------------

    elif bundle_type == "2 For X":
        # Apply moderate discount (15–30%) for value-driven bundles
        discount_multiplier = random.uniform(0.8, 0.9)
        bundle_price = round(max(total_price * discount_multiplier, total_cost), 1)
        discount_value = round(total_price - bundle_price, 2)

    # ---------------------------------------------------------
    # Buy N Save X
    # ---------------------------------------------------------

    elif bundle_type == "Buy N Save X":
        # Apply aggressive discount (15–25%) for high-incentive promotions
        capped_discount = total_price * random.uniform(0.15, 0.25)
        bundle_price = round(max(total_price - capped_discount, total_cost), 2)
        discount_value = round(total_price - bundle_price, 2)

    else:
        raise ValueError(f"Unknown bundle type: {bundle_type}")

    bundle_price = round(bundle_price, 2)
    discount_value = round(discount_value, 2)

    # Prevent edge cases
    if bundle_price <= 0:
        bundle_price = round(total_cost * 1.01, 2)
        discount_value = round(total_price - bundle_price, 2)

    if discount_value >= bundle_price:
        discount_value = round(bundle_price * 0.49, 2)

    discount_value = max(discount_value, 0.0)

    return bundle_price, discount_value


def split_window(start: pd.Timestamp, end: pd.Timestamp):
    """
    Splits a date range into 2–3 consecutive pricing phases.

    Rules:
    - Each phase lasts at least MIN_PHASE_DAYS.
    - The range must be large enough to split.
    - PROMO (if present) sits between LAUNCH and EOL.
    """
    total_days = (end - start).days

    if start > end:
        return [(start, start, "LAUNCH")]

    if total_days < MIN_WINDOW_FOR_SPLIT:
        return [(start, end, "LAUNCH")]

    phases = []

    # --- Phase 1: LAUNCH (30–50 % of total window, minimum MIN_PHASE_DAYS) ---
    launch_days = max(MIN_PHASE_DAYS, int(total_days * random.uniform(0.30, 0.50)))
    launch_end = start + timedelta(days=launch_days - 1)
    launch_end = min(launch_end, end)
    phases.append((start, launch_end, "LAUNCH"))

    remaining_start = launch_end + timedelta(days=1)

    if remaining_start > end:
        return phases

    remaining_days = (end - remaining_start).days

    # --- Phase 2 (optional): PROMO ---
    if random.random() < 0.60 and remaining_days >= MIN_PHASE_DAYS * 2:
        promo_days = max(
            MIN_PHASE_DAYS, int(remaining_days * random.uniform(0.30, 0.55))
        )
        promo_end = remaining_start + timedelta(days=promo_days - 1)
        promo_end = min(promo_end, end)
        phases.append((remaining_start, promo_end, "PROMO"))
        remaining_start = promo_end + timedelta(days=1)

        if remaining_start > end:
            return phases

        remaining_days = (end - remaining_start).days

    # ──- Phase 3: EOL (consume whatever remains, if any) ---
    if remaining_days >= MIN_PHASE_DAYS:
        phases.append((remaining_start, end, "EOL"))
    else:
        # Not enough room for a proper EOL — extend the last phase to the end
        phases[-1] = (phases[-1][0], end, phases[-1][2])

    validated = []
    for s, e, label in phases:
        if s > e:
            e = s  # collapse to a single day phase rather than invert
        validated.append((s, e, label))

    return validated


def phase_prices(base_price: float, base_discount: float, phases: list):
    """
    Generates phase prices and discounts.

    Rules:
    - Prices can only stay flat or decrease (LAUNCH ≥ PROMO ≥ EOL).
    - Discounts increase slightly across phases.
    - Each phase respects its maximum discount cap.
    """
    # Fixed reference throughout
    retail_total = base_price + base_discount
    if retail_total <= 0:
        return [(base_price, base_discount)] * len(phases)

    results = []
    # Track the current discount % so each phase steps from the previous one
    current_discount_pct = base_discount / retail_total

    for _, _, label in phases:
        if label == "LAUNCH":
            # LAUNCH price is exactly what calculate_bundle_pricing produced
            phase_discount_pct = current_discount_pct

        elif label == "PROMO":
            # Small step down from LAUNCH
            extra = random.uniform(0.0, PHASE_STEP["PROMO"])
            phase_discount_pct = min(
                current_discount_pct + extra,
                MAX_DISCOUNT_PCT["PROMO"],
            )
            current_discount_pct = phase_discount_pct

        else:  # EOL
            # Small step down from previous phase
            extra = random.uniform(0.0, PHASE_STEP["EOL"])
            phase_discount_pct = min(
                current_discount_pct + extra,
                MAX_DISCOUNT_PCT["EOL"],
            )
            current_discount_pct = phase_discount_pct

        phase_discount = round(retail_total * phase_discount_pct, 2)
        phase_price = round(retail_total - phase_discount, 2)

        # Ensure discount is lesser than price
        if phase_price <= 0:
            phase_price = round(retail_total * 0.01, 2)
            phase_discount = round(retail_total - phase_price, 2)

        if phase_discount >= phase_price:
            phase_discount = round(phase_price * 0.49, 2)

        phase_discount = max(phase_discount, 0.0)

        results.append((phase_price, phase_discount))

    return results
