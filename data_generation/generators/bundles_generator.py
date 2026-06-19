import random
import re
from typing import Any

import pandas as pd
from faker import Faker

from data_generation.config.bundles_config import BUNDLE_DEFINITIONS
from data_generation.config.generation_config import LIMIT_BUNDLE_ITEMS, NUM_BUNDLES
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.bundles.bundle_lifecycle_service import bundle_lifecycle
from data_generation.services.bundles.bundle_pricing_service import (
    calculate_bundle_pricing,
    phase_prices,
    split_window,
)
from data_generation.services.bundles.bundle_selection_service import (
    select_products_for_bundle,
)
from data_generation.utils.io_utils import save

fake = Faker()


@register("bundles_generator")
def bundles_generator(ctx: GenerationContext):

    # ---------------------------
    # Storage
    # ---------------------------

    bundles: list[dict[str, Any]] = []
    bundle_pricings: list[dict[str, Any]] = []
    bundle_items: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    pricing_counter = 1
    while len(bundles) < NUM_BUNDLES:
        bundle_id = f"BUNDLE{len(bundles) + 1:03d}"

        # --- Bundle Definition ---
        bundle_type = random.choice(list(BUNDLE_DEFINITIONS.keys()))
        bundle_name = random.choice(list(BUNDLE_DEFINITIONS[bundle_type].keys()))
        allowed_categories = BUNDLE_DEFINITIONS[bundle_type][bundle_name]

        # --- Bundle-specific Quantity Logic ---
        buy_quantity = None
        if bundle_type in ("Buy One, Get One", "2 For X"):
            buy_quantity = 2
        elif bundle_type == "Buy N Save X":
            # Retract N (purchase quantity) from bundle name
            n_match = re.search(r"Buy (\d+)", bundle_name)
            buy_quantity = int(n_match.group(1)) if n_match else 1

        # --- Bundle Product Selection ---
        result = select_products_for_bundle(
            ctx, bundle_type, allowed_categories, buy_quantity
        )

        if not result:
            continue

        selected_products, selected_categories = result

        # Skip if no valid product combination is found
        if not selected_products:
            continue

        # --- Bundle Pricing ---
        bundle_price, discount_value = calculate_bundle_pricing(
            ctx,
            bundle_type,
            selected_products,
        )

        # --- Bundle Lifecycle ---
        effective_start_date, effective_end_date = bundle_lifecycle(
            ctx, selected_products
        )
        if effective_start_date is None or effective_end_date is None:
            continue

        # --- Generate historical pricing rows ---
        phases = split_window(
            pd.Timestamp(effective_start_date),
            pd.Timestamp(effective_end_date),
        )
        phase_price_rows = phase_prices(
            bundle_price,
            discount_value,
            phases,
        )
        # --- Store Bundle Pricing Records ---
        for (phase_start, phase_end, phase_label), (phase_price, phase_discount) in zip(
            phases, phase_price_rows
        ):
            bundle_pricings.append(
                {
                    "bundle_pricing_id": f"BPRICE{pricing_counter:06d}",
                    "bundle_id": bundle_id,
                    "bundle_price": phase_price,
                    "discount_value": phase_discount,
                    "effective_start_date": phase_start.date(),
                    "effective_end_date": phase_end.date(),
                    "pricing_phase": phase_label,
                }
            )
            pricing_counter += 1

        final_discount_value = phase_price_rows[-1][1]  # EOL or last phase
        final_bundle_price = phase_price_rows[-1][0]  # EOL or last phase

        if bundle_type == "2 For X":
            # Update bundle name to reflect actual promotional price
            bundle_name = re.sub(
                r"2 for \$X", f"2 for ${final_bundle_price:.2f}", bundle_name
            )

        elif bundle_type == "Buy N Save X":
            # Update bundle name to reflect actual savings
            bundle_name = re.sub(
                r"Save \$X", f"Save ${final_discount_value:.2f}", bundle_name
            )

        # --- Store Bundle Records ---
        bundles.append(
            {
                "bundle_id": bundle_id,
                "bundle_name": bundle_name,
                "bundle_type": bundle_type,
                "categories": selected_categories,
            }
        )

        # --- Store Bundle Item Records ---
        for product_id, quantity in selected_products:
            bundle_items.append(
                {
                    "bundle_id": bundle_id,
                    "product_id": product_id,
                    "quantity": quantity,
                }
            )

        if len(bundle_items) > LIMIT_BUNDLE_ITEMS:
            break

    save(pd.DataFrame(bundles), "bundles_raw.csv")
    save(pd.DataFrame(bundle_pricings), "bundle_pricings_raw.csv")
    save(pd.DataFrame(bundle_items), "bundle_items_raw.csv")
