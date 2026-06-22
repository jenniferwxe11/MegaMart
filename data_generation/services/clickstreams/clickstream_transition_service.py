import math
import random
from typing import TypeAlias

from data_generation.config.clickstreams_config import (
    MISSION_TRANSITION_MULTIPLIERS,
    PROMOTION_TYPE_MULTIPLIER,
    SEASONAL_UPLIFT,
)
from data_generation.config.store_products_config import ESSENTIAL_CATEGORIES
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_product_stock_status,
)
from data_generation.utils.date_time_utils import (
    get_day_type,
    get_pay_cycle,
    get_seasonal_event,
    get_time_of_day,
)

# --------------------------------------
# Event Transition Probability Functions
# --------------------------------------
TransitionMatrix: TypeAlias = dict[str, dict[str, float]]


def apply_seasonal_uplift(
    timestamp,
    transition_probability: TransitionMatrix,
    progress: float,
) -> TransitionMatrix:
    """
    Adjusts temporal effects to transition probabilities.

    Factors:
    - Time of day
    - Day type (weekday/weekday)
    - Payday
    - Seasonal events

    Effects:
    - Boost add to cart
    - Boost checkout progression
    - Boost conversion
    """
    time_of_day = get_time_of_day(timestamp)
    day_type = get_day_type(timestamp)
    pay_cycle = get_pay_cycle(timestamp)
    season, _ = get_seasonal_event(timestamp)

    for s in [time_of_day, day_type, pay_cycle, season]:
        if not s:
            continue

        uplift = SEASONAL_UPLIFT.get(s)

        if not uplift:
            continue

        # Seasonal increase for add to cart uplift
        atc_range: tuple[float, float] = uplift.get("atc_mult", (1.0, 1.0))
        low_atc, high_atc = atc_range
        atc_multiplier = random.uniform(low_atc, high_atc)
        transition_probability["Product View"]["Add to Cart"] *= atc_multiplier

        # Seasonal increase for checkout uplift
        checkout_range: tuple[float, float] = uplift.get("checkout_mult", (1.0, 1.0))
        low_checkout, high_checkout = checkout_range
        checkout_multiplier = random.uniform(low_checkout, high_checkout)
        checkout_multiplier *= 1 + 0.5 * progress
        transition_probability["Cart View"]["Checkout Start"] *= checkout_multiplier

        # Seasonal increase for conversion uplift
        conversion_range: tuple[float, float] = uplift.get(
            "conversion_mult", (1.0, 1.0)
        )
        low_conversion, high_conversion = conversion_range
        conversion_multiplier = random.uniform(low_conversion, high_conversion)
        transition_probability["Checkout Start"][
            "Payment Attempt"
        ] *= conversion_multiplier

    return transition_probability


def promotion_engagement_probability(promo, event_type, times_seen):
    """
    Probability that a user engages with a promotion after being exposed to it.

    This models user's attention and initial interest.

    Factors:
    - Relevance: how contextually appropriate the promotion is for the current page (event type)
    - Mechanic strength: attractiveness of the promotion type
    - Exposure curve:
        - Early exposures -> curiosity increases engagement
        - Repeated exposures -> attention fatigue reduces engagement
    """
    base = 0.03

    scope = promo.get("promotion_scope", None)
    mechanic = promo.get("promotion_mechanic", None)
    value = promo.get("promotion_value", 0)

    # --- Contextual Relevance ---
    relevance_range = (0.0, 0.0)

    if scope == "cart" and event_type in ["Cart View", "Checkout Start"]:
        relevance_range = (0.2, 0.35)
    elif scope == "category" and event_type in ["Category View", "Product View"]:
        relevance_range = (0.1, 0.2)
    elif scope == "product" and event_type == "Product View":
        relevance_range = (0.2, 0.35)
    elif scope == "bundle" and event_type == "Product View":
        relevance_range = (0.18, 0.3)

    relevance_boost = random.uniform(*relevance_range)

    # --- Promotion Attractiveness ---
    if mechanic == "percentage_discount":
        mechanic_boost = 0.05 + 0.002 * value

    elif mechanic == "dollar_discount":
        mechanic_boost = 0.04 + 0.01 * min(value, 5)

    elif mechanic == "bundle":
        mechanic_boost = 0.06 + 0.015 * min(value, 10)
    else:
        mechanic_boost = 0.0

    # --- Exposure Curve (Curiosity -> Fatigue) ---
    exposure_effect = 0.12 * times_seen * math.exp(-0.6 * times_seen)

    # Final probability
    p = base + relevance_boost + mechanic_boost + exposure_effect

    return min(p, 0.9)


def promotion_perception_accuracy(promo):
    """
    Simulates the probability that a user correctly understands a promotion after engaging with it.

    Models cognitive clarity of user.

    Effects:
    - Complex promortions are more likely to be misunderstood or ignored
    - Misunderstood/ignored promotions have no behavioural impact

    Returns:
    - Probability of correct understanding
    """
    mechanic = promo.get("promotion_mechanic")

    if mechanic == "percentage_discount":
        understand_prob = 0.95
    elif mechanic == "dollar_discount":
        understand_prob = 0.9
    elif mechanic == "bundle":
        # Bundles are confusing
        understand_prob = 0.85
    else:
        understand_prob = 0.9

    return understand_prob


def apply_promotion_uplift(
    transition_probability: TransitionMatrix,
    selected_promotions: list[dict],
    seen_promotions: dict[str, int],
    seen_promo_types: dict[str, int],
    progress: float,
) -> TransitionMatrix:
    """
    Applies behavioural impact of promotions on user decisions.

    This models decision influence after engagement and understanding.

    Key Concepts:
    - Selection stage (Did I noticed it?)
    - Perception stage (Did I understand it?)
    - Uplift stage (Does it change my behaviour?)

    Factors:
    - Promotion type effect (Add to Cart (ATC) vs Checkout vs Remove from Cart impact)
    - Repeated exposure fatigue (reduced influence)
    - Promotion type saturation (overexposure to similar promotions)
    - Promotion stacking (diminishing returns when multiple promotions exist)
    - Funnel sensitivity:
        - Product View → Add to Cart: impulsive, highly promotion-sensitive
        - Cart View → Checkout Start: more rational, moderate sensitivity
        - Cart View → Remove from Cart: friction-driven, inverse sensitivity to promotions and highly affected by fatigue

    """
    if not selected_promotions:
        return transition_probability

    total_atc_multiplier = 1.0
    total_checkout_multiplier = 1.0
    total_remove_multiplier = 1.0

    for promo in selected_promotions:
        promotion_id = promo.get("promotion_id")
        promo_type = promo.get("promotion_mechanic")

        if not isinstance(promo_type, str):
            continue
        if promo_type not in PROMOTION_TYPE_MULTIPLIER:
            continue
        if not isinstance(promotion_id, str):
            continue

        # --- Base Effect - Promo Type ---
        promo_config = PROMOTION_TYPE_MULTIPLIER[promo_type]

        atc_range: tuple[float, float] = promo_config["atc_multiplier"]  # type: ignore[assignment]
        low_atc, high_atc = atc_range
        atc_multiplier = random.uniform(low_atc, high_atc)

        checkout_range: tuple[float, float] = promo_config["checkout_multiplier"]  # type: ignore[assignment]
        low_checkout, high_checkout = checkout_range
        checkout_multiplier = random.uniform(low_checkout, high_checkout)

        remove_range: tuple[float, float] = promo_config["remove_multiplier"]  # type: ignore[assignment]
        low_remove, high_remove = remove_range
        remove_multiplier = random.uniform(low_remove, high_remove)

        # stronger retention
        if promo_type == "bundle":
            remove_multiplier *= 0.7

        # Checkout depends on funnel progress
        checkout_multiplier *= 0.4 + 0.6 * progress

        # --- Behavioural Fatigue ---
        times_seen = seen_promotions.get(promotion_id, 0)
        type_seen = seen_promo_types.get(promo_type, 0)

        fatigue = math.exp(-0.25 * times_seen) * math.exp(-0.1 * type_seen)

        atc_multiplier *= fatigue
        checkout_multiplier *= 0.7 + 0.3 * fatigue
        remove_multiplier *= 1.0 + (1 - fatigue) * 0.5

        total_atc_multiplier *= atc_multiplier
        total_checkout_multiplier *= checkout_multiplier
        total_remove_multiplier *= remove_multiplier

    # --- Promotion Stacking (Diminishing Returns) ---
    stack_multiplier = 1.0 + 0.25 * (1 - math.exp(-0.8 * len(selected_promotions)))

    # Apply add to cart effect
    if (
        "Product View" in transition_probability
        and "Add to Cart" in transition_probability["Product View"]
    ):
        transition_probability["Product View"]["Add to Cart"] *= (
            total_atc_multiplier * stack_multiplier
        )
        transition_probability["Product View"]["Add to Cart"] = min(
            transition_probability["Product View"]["Add to Cart"], 0.9
        )

    # Apply checkout effect
    if (
        "Cart View" in transition_probability
        and "Checkout Start" in transition_probability["Cart View"]
    ):
        transition_probability["Cart View"]["Checkout Start"] *= (
            total_checkout_multiplier * stack_multiplier
        )
        transition_probability["Cart View"]["Checkout Start"] = min(
            transition_probability["Cart View"]["Checkout Start"], 0.9
        )

    # Apply remove from cart effect
    if (
        "Cart View" in transition_probability
        and "Remove from Cart" in transition_probability["Cart View"]
    ):
        transition_probability["Cart View"]["Remove from Cart"] *= (
            total_remove_multiplier / stack_multiplier
        )
        transition_probability["Cart View"]["Remove from Cart"] = max(
            transition_probability["Cart View"]["Remove from Cart"], 0.05
        )

    return transition_probability


def apply_stock_status_uplift(
    ctx,
    transition_probability: TransitionMatrix,
    store_id: str,
    product_id: str,
    timestamp,
) -> TransitionMatrix:
    """
    Adjusts user behaviour based on product stock availability.

    Rules:
    - Out of Stock -> Remove add to cart option, encourage browsing alternatives
    - Low Stock -> Urgency boost, increase add to cart probability
    - In Stock -> Slight positive purchase bias
    """
    if product_id:
        stock_status = get_product_stock_status(ctx, store_id, product_id, timestamp)

        if stock_status == "Out of Stock":
            transition_probability["Product View"].pop("Add to Cart", None)
            transition_probability["Product View"]["Home View"] *= 1.2
            transition_probability["Product View"]["Category View"] *= 1.3
            transition_probability["Product View"]["Search View"] *= 1.2

        elif stock_status == "Low Stock":
            transition_probability["Product View"]["Add to Cart"] *= 1.2

        elif stock_status == "In Stock":
            transition_probability["Product View"]["Add to Cart"] *= 1.1

    return transition_probability


def get_base_transition_probability(
    transition_probability: TransitionMatrix,
    customer_segment: str,
    has_treatment: bool,
) -> TransitionMatrix:
    """
    Applies static modifiers to transition probabilities.

    Factors:
    - Customer Segment
    - Campaign exposure

    Used as baseline before dynamic adjustments.
    """

    if has_treatment:
        # Increase add to cart rate for treatment group
        transition_probability["Product View"]["Add to Cart"] *= 1.1

        # Increase checkout uplift for treatment group
        transition_probability["Cart View"]["Checkout Start"] *= 1.1

        # Increase conversion uplift for treatment group
        transition_probability["Checkout Start"]["Payment Attempt"] *= 1.1

    if customer_segment == "High Spenders":
        transition_probability["Product View"]["Add to Cart"] *= 1.1
        transition_probability["Cart View"]["Checkout Start"] *= 1.1

    elif customer_segment == "Budget Shoppers":
        # More browsing, less conversion
        transition_probability["Product View"]["Add to Cart"] *= 0.9
        transition_probability["Cart View"]["Checkout Start"] *= 0.9
        transition_probability["Product View"]["Search View"] *= 1.1

    elif customer_segment == "Churn Risk Customers":
        # Lower engagement overall
        transition_probability["Product View"]["Add to Cart"] *= 0.85
        transition_probability["Cart View"]["Checkout Start"] *= 0.85

    return transition_probability


def apply_mission_bias(
    event_transition_probability: TransitionMatrix,
    mission_choice: str,
    previous_event_type: str | None,
    progress: float,
) -> TransitionMatrix:
    """
    Applies mission driven intent bias.

    Effects:
    - Exploratory missions -> more browsing
    - Purchase driven missions -> stronger funnel progression
    """
    if (
        not previous_event_type
        or previous_event_type not in event_transition_probability
    ):
        return event_transition_probability

    event_transitions = event_transition_probability[previous_event_type]
    mission_multipliers = MISSION_TRANSITION_MULTIPLIERS.get(mission_choice, {})
    for event, multiplier in mission_multipliers.items():
        if event in event_transitions:
            if event == "Checkout Start":
                multiplier *= 0.3 + 0.7 * progress
            event_transition_probability[previous_event_type][event] *= multiplier

    return event_transition_probability


def apply_purchase_progress_bias(
    event_transition_probability: TransitionMatrix,
    previous_event_type: str,
    previous_category: str,
    events: list[str],
    progress: float,
) -> TransitionMatrix:
    """
    Adjusts transition probabilities dynamically based on
    cart progression and contextual intent.

    Cart Progression:
    - Early stage: encourage browsing, add to cart
    - Mid stage: moderate checkout
    - Late stage: encourage checkout, reduce browsing

    Contextual Intent:
    - Higher purchase intent for necessity-driven items (essential categories)
    """
    if (
        not previous_event_type
        or previous_event_type not in event_transition_probability
    ):
        return event_transition_probability

    add_streak = events.count("Add to Cart")

    if progress < 0.5:
        # Reinforce add to cart behaviour if user is in add streak and has not added enough items yet
        if add_streak >= 2:
            if "Add to Cart" in event_transition_probability[previous_event_type]:
                event_transition_probability[previous_event_type]["Add to Cart"] *= 2.0
        # Encourage add to cart behaviour indirectly
        if "Product View" in event_transition_probability[previous_event_type]:
            event_transition_probability[previous_event_type]["Product View"] *= 2.0
        if "Cart View" in event_transition_probability[previous_event_type]:
            event_transition_probability[previous_event_type]["Cart View"] *= 0.85
        # Discourage checkout if cart is not ready
        if "Checkout Start" in event_transition_probability[previous_event_type]:
            event_transition_probability[previous_event_type]["Checkout Start"] *= 0.3
    elif progress < 0.8:
        if "Checkout Start" in event_transition_probability[previous_event_type]:
            event_transition_probability[previous_event_type]["Checkout Start"] *= 0.5
    else:
        # Encourage checkout
        if "Checkout Start" in event_transition_probability[previous_event_type]:
            event_transition_probability[previous_event_type]["Checkout Start"] *= 2.0
            # Discourage further browsing
            for k in ["Product View", "Category View", "Search View"]:
                if event_transition_probability[previous_event_type].get(k):
                    event_transition_probability[previous_event_type][k] *= 0.6

    if previous_event_type == "Product View" and previous_category:
        if previous_category in ESSENTIAL_CATEGORIES:
            if "Add to Cart" in event_transition_probability.get(
                previous_event_type, {}
            ):
                event_transition_probability[previous_event_type]["Add to Cart"] *= 1.1

    return event_transition_probability


def normalise_probability(
    transition_probability: TransitionMatrix,
) -> TransitionMatrix:
    """
    Normalises transition probabilities by rescaling their sum to 100%.
    """
    for event, transitions in transition_probability.items():
        total = sum(transitions.values())
        if total > 0:
            normalized_transitions = {}
            for next_event, prob in transitions.items():
                normalized_transitions[next_event] = prob / total
            transition_probability[event] = normalized_transitions
    return transition_probability
