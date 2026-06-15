import random

import pandas as pd

from data_generation.config.campaigns_config import (
    CAMPAIGN_PEAK_CATEGORIES,
    CATEGORY_CODE_MAP,
)
from data_generation.config.customers_config import SEGMENT_CATEGORY_BIAS
from data_generation.config.promotions_config import (
    BUNDLE_CAMPAIGN_COMPATIBILITY,
    CAMPAIGN_PROMOTION_STRATEGY,
    CATEGORY_DOLLAR_DISCOUNT_CAP,
    CATEGORY_PERCENT_DISCOUNT_RANGE,
    CATEGORY_PROMOTION_PROB,
    CHANNEL_PROMOTION_COMPATIBILITY,
    MIN_SPEND_FOR_FREE_SHIPPING,
    MIN_SPEND_PER_CATEGORY,
    PROMO_NAME_TEMPLATES,
)

# ---------------------------
# Helper Functions
# ---------------------------


def safe_date_window(start, end, data_end_date):
    """
    Returns (start, end) as pd.Timestamps, guaranteeing start <= end.
    If they would invert, end is clamped to start (zero-length window is
    still valid for the dbt test effective_start_date <= effective_end_date).
    """
    start = pd.Timestamp(start)
    end = pd.Timestamp(min(pd.Timestamp(end), pd.Timestamp(data_end_date)))
    if end < start:
        end = start
    return start, end


def select_promotion_mechanics(campaign_type, channels):
    """
    Selects promotion mechanics that aligned with:
    - Campaign intent (strategy driven)
    - Channel constraints (what each channel can support)

    Rules:
    - Prioritise primary promotion mechanics
    - Pair primary with compatible secondary promotion mechanics to introduce variety
    """
    # Determine how many promotions this campaign should carry (strategy driven)
    strategy = CAMPAIGN_PROMOTION_STRATEGY[campaign_type]
    min_promo, max_promo = strategy.get("promo_count", (1, 2))
    num_promos = random.randint(min_promo, max_promo)

    selected_promotions = []
    allowed_promotions = set()

    # Aggregate all mechanics allowed by chosen channels
    for channel in channels:
        allowed_promotions.update(CHANNEL_PROMOTION_COMPATIBILITY.get(channel, []))

    # Filter primary mechanics by compatibility
    primary = []
    for promo in strategy["primary"]:
        if promo in allowed_promotions:
            primary.append(promo)

    # Prioritise primary mechanics
    if primary:
        selected_promotions.append(random.choice(primary))

    # Secondary pool includes secondary + unused primary
    secondary = []
    for promo in strategy["secondary"]:
        if promo in allowed_promotions:
            secondary.append(promo)

    for promo in primary:
        if promo not in selected_promotions:
            secondary.append(promo)

    # Fill remaining slots with compatible secondary mechanics for variety
    remaining = num_promos - len(selected_promotions)
    if secondary and remaining > 0:
        selected_promotions.extend(
            random.sample(secondary, k=min(remaining, len(secondary)))
        )

    return selected_promotions


def select_category(
    campaign_type=None,
    season=None,
    target_segment=None,
):
    """
    Selects category based on:
    - Campaign type (seasonal)
    - Customer segment preference
    """
    # Seasonal campaigns prioritise seasonally relevant categories
    if campaign_type == "Seasonal" and season:
        base_categories = CAMPAIGN_PEAK_CATEGORIES[campaign_type].get(season, [])
    else:
        base_categories = CAMPAIGN_PEAK_CATEGORIES.get(campaign_type, [])

    # Non seasonal campaign: Use categories that are more likely to go on promotion
    if not base_categories:
        base_categories = list(CATEGORY_PROMOTION_PROB.keys())

    weights = []

    # Customer category preferences
    for cat in base_categories:
        w = CATEGORY_PROMOTION_PROB.get(cat, 0.05)
        w *= SEGMENT_CATEGORY_BIAS.get(target_segment, {}).get(cat, 1)
        weights.append(w)

    # Normalize
    total = sum(weights)
    weights = [w / total for w in weights]

    return random.choices(base_categories, weights=weights, k=1)[0]


def select_product_in_category(ctx, category):
    """
    Selects a product that is in chosen category.
    """
    products_df = ctx.products.products_df

    eligible_products = products_df[products_df["category"] == category]

    if eligible_products.empty:
        return None

    return eligible_products.sample(1)["product_id"].iloc[0]


def select_active_product_in_timeframe(
    ctx,
    category,
    effective_start_date,
    effective_end_date,
):
    """
    Selects a product that is:
    - In chosen category
    - Active during the campaign window
    """
    product_with_lifecycle_df = ctx.product_lifecycles.product_with_lifecycle_df

    # Filter by chosen category and lifecycle validity
    eligible_products = product_with_lifecycle_df[
        (product_with_lifecycle_df["category"] == category)
        & (product_with_lifecycle_df["launch_date"].notna())
        & (product_with_lifecycle_df["launch_date"] <= effective_start_date)
        & (
            product_with_lifecycle_df["discontinuation_date"].isna()
            | (product_with_lifecycle_df["discontinuation_date"] >= effective_end_date)
        )
    ]

    if eligible_products.empty:
        return None

    return eligible_products.sample(1)["product_id"].iloc[0]


def select_bundle_for_campaign(
    ctx,
    campaign_type,
    effective_start_date,
    effective_end_date,
):
    """
    Selects a bundle that is:
    - Compatible with campaign type
    - Active during the campaign window
    """
    bundle_full_df = ctx.bundles.bundle_full_df

    allowed_bundle_type = BUNDLE_CAMPAIGN_COMPATIBILITY.get(campaign_type, [])

    if not allowed_bundle_type:
        return None

    eligible = bundle_full_df[
        (bundle_full_df["bundle_type"].isin(allowed_bundle_type))
        & (bundle_full_df["effective_start_date"] <= effective_start_date)
        & (bundle_full_df["effective_end_date"] >= effective_end_date)
    ]

    if eligible.empty:
        return None

    selected_bundle = eligible.sample(1).iloc[0]

    return {
        "bundle_id": selected_bundle["bundle_id"],
        "bundle_pricing_id": selected_bundle["bundle_pricing_id"],
        "bundle_price": selected_bundle["bundle_price"],
        "discount_value": selected_bundle["discount_value"],
        "effective_start_date": selected_bundle["effective_start_date"],
        "effective_end_date": selected_bundle["effective_end_date"],
        "categories": selected_bundle["categories"],
    }


def generate_promotion_value(
    ctx,
    promotion_mechanic,
    promotion_scope,
    promotion_target_id,
    category,
    campaign_type=None,
    bundle=None,
):
    """
    Generates discount value based on promotion type.
    """
    product_price_map = ctx.products.product_price_map
    products_df = ctx.products.products_df

    if promotion_mechanic == "percentage_discount":
        # Category level discount guardrails (margin protection)
        low, high = CATEGORY_PERCENT_DISCOUNT_RANGE.get(category, (5, 20))
        discount = random.randint(low, high)

        # Apply stronger incentives for clearance campaigns
        if campaign_type == "Clearance":
            discount += 10

        # Basline promos are generally weaker than campaign promos
        # to create a clear distinction in treatment effect
        if campaign_type is None:
            discount *= 0.7

        return round(min(discount, 40), 0)

    elif promotion_mechanic == "dollar_discount":

        if promotion_scope == "product":
            product_price = product_price_map.get(promotion_target_id)
            return round(random.uniform(0.1, 0.3) * product_price, 2)
        else:
            prices = products_df.loc[
                products_df["category"] == category, "selling_price"
            ]

            if prices.empty:
                return random.randint(2, 10)

            # Prevent discounts from exceeding acceptable margin thresholds
            max_price = prices.max()
            cap = CATEGORY_DOLLAR_DISCOUNT_CAP.get(category, max_price * 0.3)
            return round(random.uniform(2, min(cap, max_price * 0.4)), 2)

    elif promotion_mechanic == "free_shipping":
        return 0.0

    elif promotion_mechanic == "bundle" and bundle:
        return round(bundle["discount_value"], 2)


def generate_promotion_name(
    promotion_mechanic,
    promotion_scope,
    category=None,
    season=None,
):
    """
    Generates customer facing promotion name.
    """
    prefix = f"{season} " if pd.notna(season) else ""

    if promotion_mechanic == "free_shipping":
        return prefix + random.choice(PROMO_NAME_TEMPLATES["Free Shipping"])

    if promotion_mechanic == "bundle":
        return prefix + random.choice(PROMO_NAME_TEMPLATES["Bundle"])

    if promotion_scope == "category" and category:
        template = random.choice(PROMO_NAME_TEMPLATES["Category"])
        return prefix + template.format(category=category)

    return prefix + "Special Offer"


def get_min_spend(
    promotion_mechanic, promotion_scope, promotion_value, category, campaign_type=None
):
    """
    Determines minimum spend required to unlock promotion.

    Outcome:
    - Balances conversion with profitability
    - Encourages basket uplift
    """
    if promotion_mechanic == "free_shipping":
        return MIN_SPEND_FOR_FREE_SHIPPING.get(campaign_type, 80.0)

    if promotion_scope == "category" and category:
        # Min spend fulfilled on cart to get discount on category
        base_min_spend = MIN_SPEND_PER_CATEGORY.get(category, 0.0)

        if promotion_mechanic == "percentage_discount":
            return None

        if promotion_mechanic == "dollar_discount":
            multiplier = random.choice([1.5, 2, 2.5])
            return max(base_min_spend, promotion_value * multiplier)

    return None


def generate_discount_code(
    promotion_mechanic,
    promotion_scope,
    promotion_target_id,
    promotion_value,
    campaign_id=None,
):
    """
    Generates structured discount code.

    Implementation:
    - Encodes campaign, mechanic, and target values for traceability
    """
    parts = []

    if campaign_id:
        parts.append(campaign_id)

    parts.append(promotion_mechanic.upper())

    if promotion_target_id:
        if promotion_scope == "category":
            parts.append(CATEGORY_CODE_MAP.get(promotion_target_id))
        else:
            parts.append(promotion_target_id)

    if promotion_value and promotion_mechanic != "free_shipping":
        parts.append(str(int(promotion_value)))

    return "_".join(parts)
