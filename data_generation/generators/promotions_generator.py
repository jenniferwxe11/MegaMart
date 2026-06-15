import ast
import random
from datetime import timedelta
from typing import Any

import pandas as pd
from faker import Faker

from data_generation.config.generation_config import LIMIT_PROMOTIONS
from data_generation.config.promotions_config import (
    MECHANIC_SCOPE_RULES,
    PROMOTION_THEMES,
    STACKING_PRIORITY,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.promotions.promotion_service import (
    generate_discount_code,
    generate_promotion_name,
    generate_promotion_value,
    get_min_spend,
    safe_date_window,
    select_active_product_in_timeframe,
    select_bundle_for_campaign,
    select_category,
    select_product_in_category,
    select_promotion_mechanics,
)
from data_generation.utils.io_utils import save

fake = Faker()


@register("promotions_generator")
def promotions_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    DATA_START_DATE = ctx.config.DATA_START_DATE
    DATA_END_DATE = ctx.config.DATA_END_DATE

    assert ctx.bundles is not None
    bundle_full_df = ctx.bundles.bundle_full_df

    assert ctx.product_lifecycles is not None
    product_launch_map = ctx.product_lifecycles.product_launch_map
    product_discontinuation_map = ctx.product_lifecycles.product_discontinuation_map

    assert ctx.campaigns is not None
    campaigns_df = ctx.campaigns.campaigns_df

    # ---------------------------
    # Storage
    # ---------------------------

    promotions: list[dict[str, Any]] = []

    # -------------------------------
    # Generation: Campaign Promotions
    # -------------------------------

    i = 1
    for _, campaign_row in campaigns_df.iterrows():
        if len(promotions) >= LIMIT_PROMOTIONS:
            break

        campaign_id = campaign_row["campaign_id"]
        campaign_type = campaign_row["campaign_type"]
        target_segment = campaign_row["target_segment"]
        season = campaign_row.get("season", None)
        effective_start_date = campaign_row["start_date"]
        effective_end_date = campaign_row["end_date"]
        raw_channels = campaign_row["channels"]

        if effective_end_date < effective_start_date:
            continue

        # Convert datatype
        if isinstance(raw_channels, str):
            channels = ast.literal_eval(raw_channels)
        else:
            channels = raw_channels

        promotion_mechanics = select_promotion_mechanics(campaign_type, channels)

        for promotion_mechanic in promotion_mechanics:
            promotion_id = f"PROMO{i:03d}"
            promotion_scope = random.choice(MECHANIC_SCOPE_RULES[promotion_mechanic])

            promo_start = effective_start_date
            promo_end = effective_end_date

            promotion_target_id = None
            category = None
            bundle = None

            if promotion_scope == "category":
                category = select_category(campaign_type, season, target_segment)
                promotion_target_id = category

            elif promotion_scope == "product":
                category = select_category(campaign_type, season, target_segment)
                product_id = select_active_product_in_timeframe(
                    ctx, category, effective_start_date, effective_end_date
                )
                if product_id is None:
                    continue
                promotion_target_id = product_id

            elif promotion_scope == "bundle":
                bundle = select_bundle_for_campaign(
                    ctx, campaign_type, promo_start, promo_end
                )
                if bundle is None:
                    continue

                category = random.choice(bundle["categories"])
                promotion_target_id = bundle["bundle_id"]
                promo_start = max(
                    pd.Timestamp(bundle["effective_start_date"]),
                    pd.Timestamp(campaign_row["start_date"]),
                )
                promo_end = min(
                    pd.Timestamp(bundle["effective_end_date"]),
                    pd.Timestamp(campaign_row["end_date"]),
                )

            promo_start, promo_end = safe_date_window(
                promo_start, promo_end, DATA_END_DATE
            )

            promotion_value = generate_promotion_value(
                ctx,
                promotion_mechanic,
                promotion_scope,
                promotion_target_id,
                category,
                campaign_type,
                bundle,
            )

            if promotion_value is None:
                continue

            min_spend = get_min_spend(
                promotion_mechanic,
                promotion_scope,
                promotion_value,
                category,
                campaign_type,
            )

            promotion_name = generate_promotion_name(
                promotion_mechanic, promotion_scope, category, season
            )

            discount_code = generate_discount_code(
                promotion_mechanic,
                promotion_scope,
                promotion_target_id,
                promotion_value,
                campaign_id,
            )

            promotion_theme = random.choice(
                PROMOTION_THEMES.get(campaign_type, ["Special Promotion"])
            )

            # Store Campaign Promotions
            promotions.append(
                {
                    "promotion_id": promotion_id,
                    "promotion_name": promotion_name,
                    "promotion_theme": promotion_theme,
                    "campaign_id": campaign_id,
                    "promotion_mechanic": promotion_mechanic,
                    "promotion_scope": promotion_scope,
                    "promotion_target_id": promotion_target_id,
                    "promotion_value": promotion_value,
                    "min_spend": min_spend,
                    "discount_code": discount_code,
                    "effective_start_date": promo_start,
                    "effective_end_date": promo_end,
                    "priority": STACKING_PRIORITY[promotion_scope],
                }
            )
            i += 1

    # -------------------------------
    # Generation: Bundle Promotions
    # -------------------------------

    for _, bundle_row in bundle_full_df.iterrows():
        if len(promotions) >= LIMIT_PROMOTIONS:
            break

        promotion_id = f"PROMO{i:03d}"
        promotion_value = round(bundle_row["discount_value"], 2)

        b_start, b_end = safe_date_window(
            bundle_row["effective_start_date"],
            bundle_row["effective_end_date"],
            DATA_END_DATE,
        )

        # Store Bundle Promotions
        promotions.append(
            {
                "promotion_id": promotion_id,
                "promotion_name": generate_promotion_name("bundle", "bundle"),
                "promotion_theme": "Bundle Deal",
                "campaign_id": None,
                "promotion_mechanic": "bundle",
                "promotion_scope": "bundle",
                "promotion_target_id": bundle_row["bundle_id"],
                "promotion_value": promotion_value,
                "min_spend": None,
                "discount_code": generate_discount_code(
                    "bundle", "bundle", bundle_row["bundle_id"], promotion_value
                ),
                "effective_start_date": b_start,
                "effective_end_date": b_end,
                "priority": STACKING_PRIORITY["bundle"],
            }
        )
        i += 1

    # -----------------------------------
    # Generation: Non Campaign Promotions
    # -----------------------------------

    # 60–70% → non-campaign promotions (baseline)
    # 30–40% → campaign promotions (treatment)
    NUM_BASELINE_PROMOS = int(len(campaigns_df) * 1.5)

    campaign_type = None
    season = None
    target_segment = None

    for _ in range(NUM_BASELINE_PROMOS):
        if len(promotions) >= LIMIT_PROMOTIONS:
            break

        promotion_id = f"PROMO{i:03d}"

        promotion_mechanic = random.choice(
            ["percentage_discount", "dollar_discount", "free_shipping"]
        )

        promotion_scope = random.choice(MECHANIC_SCOPE_RULES[promotion_mechanic])

        promotion_target_id = None
        category = None

        if promotion_scope == "category":
            category = select_category(campaign_type, season, target_segment)
            promotion_target_id = category
            promo_start = pd.to_datetime(
                fake.date_between(
                    start_date=DATA_START_DATE, end_date=pd.Timestamp(DATA_END_DATE)
                )
            )

            promo_end = pd.to_datetime(
                min(
                    pd.Timestamp(promo_start + timedelta(days=random.randint(30, 120))),
                    pd.Timestamp(DATA_END_DATE),
                )
            )

        elif promotion_scope == "product":
            category = select_category(campaign_type, season, target_segment)
            product_id = select_product_in_category(ctx, category)
            if product_id is None:
                continue

            promotion_target_id = product_id
            launch_date = pd.to_datetime(product_launch_map.get(product_id, None))
            discontinuation_date = pd.to_datetime(
                product_discontinuation_map.get(product_id, None)
            )

            # Skip bundles with no overlapping product availability window
            if not pd.isna(launch_date) and not pd.isna(discontinuation_date):
                if launch_date > discontinuation_date:
                    continue

            # Fallback: default to global data window if lifecycle data is missing
            if pd.isna(launch_date):
                launch_date = pd.Timestamp(DATA_START_DATE)
            if pd.isna(discontinuation_date):
                discontinuation_date = pd.Timestamp(DATA_END_DATE)

            # Assign active promotion window (30–120 days)
            effective_lifecycle_end = min(
                pd.Timestamp(discontinuation_date), pd.Timestamp(DATA_END_DATE)
            )
            if launch_date > effective_lifecycle_end:
                continue

            promo_start = pd.to_datetime(
                fake.date_between(
                    start_date=launch_date, end_date=effective_lifecycle_end
                )
            )
            promo_end = pd.to_datetime(
                min(
                    pd.Timestamp(promo_start + timedelta(days=random.randint(30, 120))),
                    pd.Timestamp(discontinuation_date),
                    pd.Timestamp(DATA_END_DATE),
                )
            )

        else:
            continue

        promo_start, promo_end = safe_date_window(promo_start, promo_end, DATA_END_DATE)

        promotion_value = generate_promotion_value(
            ctx,
            promotion_mechanic,
            promotion_scope,
            promotion_target_id,
            category,
        )

        if promotion_value is None:
            continue

        min_spend = get_min_spend(
            promotion_mechanic, promotion_scope, promotion_value, category
        )

        promotion_name = generate_promotion_name(
            promotion_mechanic, promotion_scope, category
        )

        discount_code = generate_discount_code(
            promotion_mechanic,
            promotion_scope,
            promotion_target_id,
            promotion_value,
        )

        # Store Non Campaign Promotions
        promotions.append(
            {
                "promotion_id": promotion_id,
                "promotion_name": promotion_name,
                "promotion_theme": "Special Promotion",
                "campaign_id": None,
                "promotion_mechanic": promotion_mechanic,
                "promotion_scope": promotion_scope,
                "promotion_target_id": promotion_target_id,
                "promotion_value": promotion_value,
                "min_spend": min_spend,
                "discount_code": discount_code,
                "effective_start_date": promo_start,
                "effective_end_date": promo_end,
                "priority": STACKING_PRIORITY[promotion_scope],
            }
        )

        i += 1

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(promotions), "promotions_raw.csv")
