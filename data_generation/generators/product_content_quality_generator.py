import random
from datetime import timedelta
from typing import Any

import pandas as pd

from data_generation.config.generation_config import LIMIT_PRODUCT_CONTENT_QUALITY
from data_generation.config.product_content_config import (
    ADVANCE_PROB,
    CATEGORY_ATTRIBUTES,
    ENRICH_GAP,
    MAX_ENRICHMENTS,
    TIERS,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.products.product_content_quality_service import (
    generate_content_characteristics,
)
from data_generation.utils.io_utils import save


@register("product_content_quality_generator")
def product_content_quality_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    products_df = ctx.products.products_df
    product_ids = ctx.products.product_ids

    assert ctx.product_lifecycles is not None
    product_lifecycles_df = ctx.product_lifecycles.product_lifecycles_df

    # ---------------------------
    # Storage
    # ---------------------------

    product_content_quality: list[dict[str, Any]] = []
    version_counter = 1

    # ---------------------------
    # Generation
    # ---------------------------

    for product_id in product_ids:
        current_plc = product_lifecycles_df.loc[
            (product_lifecycles_df["product_id"] == product_id)
            & (product_lifecycles_df["is_current"])
        ]
        if current_plc.empty:
            # Fallback: use any row
            current_plc = product_lifecycles_df.loc[
                product_lifecycles_df["product_id"] == product_id
            ]
        if current_plc.empty:
            continue

        plc_row = current_plc.iloc[0]
        lifecycle_status = plc_row["status"]
        launch_date = pd.Timestamp(plc_row["launch_date"])

        # Get expected attribute count of product based on category
        category = products_df.loc[
            products_df["product_id"] == product_id, "category"
        ].iloc[0]
        category_attributes = CATEGORY_ATTRIBUTES.get(category, [])
        total_attributes = len(category_attributes)

        if lifecycle_status == "New":
            # Reflect real world lag in content enrichment
            start_tier = "Poor"
        else:
            # Established products can start at any tier, but Poor is still common
            start_tier = random.choices(TIERS, weights=[0.35, 0.35, 0.20, 0.10], k=1)[0]

        current_tier = start_tier
        current_date = launch_date  # first version is effective from launch

        version_chain = []  # list of (tier, valid_from)
        version_chain.append((current_tier, current_date))

        for _ in range(MAX_ENRICHMENTS):
            tier_idx = TIERS.index(current_tier)
            if tier_idx >= len(TIERS) - 1:
                break  # already at Excellent

            # Does an enrichment happen?
            if random.random() > ADVANCE_PROB.get(current_tier, 0.0):
                break

            # When does the next enrichment happen?
            gap_days = random.randint(*ENRICH_GAP)
            next_date = current_date + timedelta(days=gap_days)

            # Don't exceed simulation window
            if next_date > pd.Timestamp(ctx.config.DATA_END_DATE):
                break

            current_tier = TIERS[tier_idx + 1]
            current_date = next_date
            version_chain.append((current_tier, current_date))

        for idx, (tier, valid_from) in enumerate(version_chain):
            is_last = idx == len(version_chain) - 1
            valid_to = None if is_last else version_chain[idx + 1][1]

            content = generate_content_characteristics(tier, total_attributes)

            # --- Store Product Content Quality Record ---
            product_content_quality.append(
                {
                    "content_version_id": f"PCQ{version_counter:07d}",
                    "product_id": product_id,
                    "quality_tier": tier,
                    "has_image": content["has_image"],
                    "image_count": content["image_count"],
                    "image_quality_score": content["image_quality_score"],
                    "has_nutritional_info": content["has_nutritional_info"],
                    "has_description": content["has_description"],
                    "description_length": content["description_length"],
                    "missing_attribute_count": content["missing_attribute_count"],
                    "valid_from": valid_from.date(),
                    "valid_to": valid_to.date() if valid_to else None,
                    "is_current": is_last,
                }
            )
            version_counter += 1

        if len(product_content_quality) >= LIMIT_PRODUCT_CONTENT_QUALITY:
            break

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(product_content_quality), "product_content_quality_raw.csv")
