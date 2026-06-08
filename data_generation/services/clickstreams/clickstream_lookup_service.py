import random
import re

import pandas as pd
from faker import Faker

from data_generation.config.clickstreams_config import (
    CATEGORY_DEMAND_DISTRIBUTION,
    CATEGORY_EXPOSURE_MULTIPLIER,
    IN_STOCK_STATUS,
)
from data_generation.config.customers_config import SEGMENT_CATEGORY_BIAS

fake = Faker()
# ------------------------------
# Data Access & Lookup Functions
# ------------------------------


def get_location(
    ctx,
    customer_id,
):
    """
    Assigns browsing location.

    Behaviour:
    - 80% -> customer's usual area
    - 15% -> nearby area (same region)
    - 5% -> random (travel/VPN/anomaly)
    """
    customers_df = ctx.customers.customers_df
    region_area_map = ctx.region_areas.region_area_map
    all_areas = ctx.reference_data.locations

    customer_row = customers_df.loc[customers_df["customer_id"] == customer_id]

    if customer_row.empty:
        return random.choice(all_areas)

    row = customer_row.iloc[0]
    region = row.get("region")
    area = row.get("area")

    if pd.isna(region) or pd.isna(area):
        return random.choice(all_areas)

    r = random.random()

    # 80%: home area
    if r < 0.8:
        return area

    # 15%: same region
    elif r < 0.95:
        areas_in_region = region_area_map.get(region, [])
        if areas_in_region:
            return random.choice(areas_in_region)
        return random.choice(all_areas)

    # 5%: anomaly / travel
    return random.choice(all_areas)


def get_search_term(ctx):
    """
    Generates realistic search queries.
    - Known terms (brands, categories)
    - Random/noisy terms (to simulate real users)

    Not all searches are clean or structured
    """
    SEARCH_TERMS = ctx.reference_data.search_terms
    # assert SEARCH_TERMS, "SEARCH_TERMS must not be empty"
    if random.random() < 0.2:
        return fake.word().lower().replace(" ", "+")
    search_term = random.choice(SEARCH_TERMS)
    words = search_term.split()
    term_length = random.randint(1, min(2, len(words)))
    start_index = random.randint(0, len(words) - term_length)
    return (
        " ".join(words[start_index : start_index + term_length])
        .replace(" ", "+")
        .replace("&", "")
    )


def slugify(text):
    """
    Converts text into a standardized, URL friendly identifier.
    """
    text = text.lower()
    text = re.sub(r"[&]", "and", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def get_random_product_from_search_term(ctx, search_term):
    """
    Selects a product from search results.

    Behaviour:
    - Matches product using partial, case-insensitive search
    - Handles incomplete or noisy queries

    Assumption:
    - User clicks on a random product from matching results
    """
    products_df = ctx.products.products_df

    term = search_term.replace("+", " ").strip()
    term = re.escape(term)
    matching_product_ids = products_df[
        products_df["product_name"].str.contains(
            term,
            case=False,
            na=False,
            regex=True,
        )
    ]["product_id"].tolist()
    if matching_product_ids:
        return matching_product_ids
    return None


def get_segment_category(customer_segment):
    """
    Selects product category based on customer segment.

    Behaviour:
    - Base category popularity adjusted by segment bias
    - High spenders -> Premium categories
    - Budget users -> Essentials
    """
    assert (
        CATEGORY_DEMAND_DISTRIBUTION
    ), "CATEGORY_DEMAND_DISTRIBUTION must not be empty"

    # How populate the category is
    base = CATEGORY_DEMAND_DISTRIBUTION.copy()

    # User preference
    segment_bias = SEGMENT_CATEGORY_BIAS.get(customer_segment, {})

    adjusted_weights = {}

    # CATEGORY_EXPOSURE_MULTIPLIER - merchandising / visibility / placement - more likely to be browsed
    for category, frequency in base.items():
        bias_multiplier = segment_bias.get(category, 1.0)
        adjusted_weights[category] = (
            frequency
            * bias_multiplier
            * CATEGORY_EXPOSURE_MULTIPLIER.get(category, 1.0)
        )

    category = random.choices(
        list(adjusted_weights.keys()), weights=list(adjusted_weights.values()), k=1
    )[0]

    return category


def get_product_stock_status(ctx, store_id, product_id, timestamp):
    """
    Retrieves product stock status at a given time.
    - Uses latest weekly snapshot before timestamp

    Returns:
    - "In Stock"
    - "Low Stock"
    - "Out of Stock"
    """
    stock_snapshots_df = ctx.stock_snapshots.stock_snapshots_df

    stockout_row = stock_snapshots_df[
        (stock_snapshots_df["store_id"] == store_id)
        & (stock_snapshots_df["product_id"] == product_id)
        & (stock_snapshots_df["week_start_date"] <= timestamp)
    ]
    if stockout_row.empty:
        return "In Stock"

    latest_row = stockout_row.sort_values("week_start_date", ascending=False).iloc[0]
    return latest_row["stock_status"]


def get_random_product_from_category(ctx, category):
    """
    Selects a random product from a given category.
    """
    category_to_products = ctx.products.category_to_products

    product_ids = category_to_products.get(category, [])

    if not product_ids:
        return None

    return random.choice(product_ids)


def get_random_in_stock_product_from_category(ctx, category, store_id, timestamp):
    """
    Selects a random in stock product from a given category.
    """
    category_to_products = ctx.products.category_to_products

    product_ids = category_to_products.get(category, [])

    in_stock_products = []

    for product_id in product_ids:
        status = get_product_stock_status(ctx, store_id, product_id, timestamp)

        if status in IN_STOCK_STATUS:
            in_stock_products.append(product_id)

    if not in_stock_products:
        return None

    return random.choice(in_stock_products)


def get_active_campaigns(ctx, customer_id, session_start_time):
    """
    Returns all active campaigns for a customer at a given time.
    """
    campaigns_df = ctx.campaigns.campaigns_df
    campaign_assignments_df = ctx.campaign_assignments.campaign_assignments_df

    if (
        campaign_assignments_df.empty
        or "customer_id" not in campaign_assignments_df.columns
    ):
        return None

    customer_campaigns = campaign_assignments_df[
        campaign_assignments_df["customer_id"] == customer_id
    ]

    if customer_campaigns.empty:
        return None

    # Merge assigned campaigns with campaign details to get start/end dates
    merged_df = customer_campaigns.merge(campaigns_df, on="campaign_id", how="left")

    # Filter active campaigns during this session
    active_campaigns = merged_df[
        (merged_df["start_date"] <= session_start_time)
        & (merged_df["end_date"] >= session_start_time)
    ]

    if active_campaigns.empty:
        return None

    return active_campaigns


def get_active_promotions(ctx, timestamp):
    """
    Identifies promotions that are active at the time of the session.
    """
    promotions_df = ctx.promotions.promotions_df

    active = promotions_df[
        (promotions_df["effective_start_date"] <= timestamp)
        & (promotions_df["effective_end_date"] >= timestamp)
    ]

    if active.empty:
        return []
    return active.to_dict("records")


def check_promotion_eligibility(ctx, timestamp, active_campaigns):
    """
    Determines which promotions are visible to the customer at a given time.

    Rules:
    - Global promos - always visible
    - Campaign promos - only visible if:
        - Customer is in Treatment group for that campaign
    """
    if active_campaigns is None:
        active_campaigns = []

    # If DataFrame → convert to list of dicts
    if hasattr(active_campaigns, "to_dict"):
        active_campaigns = active_campaigns.to_dict("records")

    # Now safe list
    if len(active_campaigns) == 0:
        active_campaigns = []

    active_promotions = get_active_promotions(ctx, timestamp)
    if not active_promotions:
        return []

    # If no active campaigns, only global promotions are eligible
    if not active_campaigns:
        return [
            promo
            for promo in active_promotions
            if not promo.get("campaign_id") or pd.isna(promo.get("campaign_id"))
        ]

    # Get active campaign ids for treatment group
    treatment_campaign_ids = {
        c["campaign_id"] for c in active_campaigns if c.get("group") == "Treatment"
    }

    eligible_promotions = []

    for promo in active_promotions:
        campaign_id = promo.get("campaign_id")

        # Global promotion
        if not promo["campaign_id"] or pd.isna(campaign_id):
            eligible_promotions.append(promo)

        # Campaign linked promotion
        if campaign_id in treatment_campaign_ids:
            eligible_promotions.append(promo)

    return eligible_promotions


def get_relevant_promotion_on_page(
    ctx,
    timestamp,
    event_type,
    category,
    product_id,
    active_campaigns,
):
    """
    Get all the relevant promotions that apply at this specific event.

    Relevance Rules:
    - Cart promotions -> only relevant during Cart View and Checkout Start
    - Category promotions -> relevant when browsing that category or related products
    - Product promotions -> most relevant on product page
    - Bundle promotions -> relevant when viewing products within that bundle
    """
    bundle_dict = ctx.bundles.bundle_dict

    # Get active promotion
    eligible_promotions = check_promotion_eligibility(ctx, timestamp, active_campaigns)

    if not eligible_promotions:
        return []

    visible_promotions = []

    for promo in eligible_promotions:
        promotion_id = promo.get("promotion_id", None)
        promotion_scope = promo.get("promotion_scope", None)
        promotion_target = promo.get("promotion_target_id", None)
        promotion_mechanic = promo.get("promotion_mechanic", None)

        # Cart promotion
        if promotion_scope == "cart":
            if event_type in ["Cart View", "Checkout Start"]:
                visible_promotions.append(
                    {
                        "promotion_id": promotion_id,
                        "promotion_scope": promotion_scope,
                        "promotion_target_id": promotion_target,
                        "promotion_mechanic": promotion_mechanic,
                        "bundle_id": None,
                    }
                )

        # Category promotion
        if promotion_scope == "category":
            if category == promotion_target and event_type in [
                "Category View",
                "Product View",
            ]:
                visible_promotions.append(
                    {
                        "promotion_id": promotion_id,
                        "promotion_scope": promotion_scope,
                        "promotion_target_id": promotion_target,
                        "promotion_mechanic": promotion_mechanic,
                        "bundle_id": None,
                    }
                )

        # Product promotion
        if promotion_scope == "product":
            if product_id == promotion_target and event_type == "Product View":
                visible_promotions.append(
                    {
                        "promotion_id": promotion_id,
                        "promotion_scope": promotion_scope,
                        "promotion_target_id": promotion_target,
                        "promotion_mechanic": promotion_mechanic,
                        "bundle_id": None,
                    }
                )

        # Bundle promotion
        if promotion_scope == "bundle":
            bundle_products = bundle_dict.get(promotion_target, {})

            # Product page match
            if product_id and product_id in bundle_products:
                visible_promotions.append(
                    {
                        "promotion_id": promotion_id,
                        "promotion_scope": promotion_scope,
                        "promotion_target_id": promotion_target,
                        "promotion_mechanic": promotion_mechanic,
                        "bundle_id": promotion_target,
                    }
                )

    return visible_promotions
