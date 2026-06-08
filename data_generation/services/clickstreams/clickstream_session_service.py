import random
from datetime import datetime, timedelta

import numpy as np

from data_generation.config.clickstreams_config import (
    DAY_WEIGHTS,
    HOUR_WEIGHTS,
    MAX_ACTIVITY_MULTIPLIER,
    MISSION_SCROLL_BIAS,
    PARETO_ALPHA,
    REACTIVATION_BY_SEGMENT,
    RETURN_PROB_BY_SEGMENT,
    SEASONAL_REACTIVATION_BOOST,
    SESSION_GAP_SCALE_BY_SEGMENT,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_active_campaigns,
)
from data_generation.utils.date_time_utils import (
    get_day_type,
    get_pay_cycle,
    get_seasonal_event,
)

# --------------------------------
# Session Initialization Functions
# --------------------------------


def generate_timestamp(ctx, start_date, end_date):
    """
    Generates a realistic session timestamp within a given date range.

    Behaviour:
    - Bias towards weekends, payday periods, evenings

    Assumption:
    - User activity is time dependent and follows predictable temporal patterns
    """
    DATA_END_DATE = ctx.config.DATA_END_DATE
    DATA_START_DATE = ctx.config.DATA_START_DATE

    # Define the start and end date range
    start = max(DATA_START_DATE, start_date)
    end = min(DATA_END_DATE, end_date)

    if start > end:
        end = start

    # Generate all possible dates in the range
    all_dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]

    # Assign weights based on weekend/weekday and payday boosts
    date_weights = []
    for d in all_dates:
        w = 1.0

        # Weekday/weekend
        week_day = get_day_type(d)
        w *= DAY_WEIGHTS.get(week_day, 1.0)

        # Payday and payday spillover boosts
        pay_day = get_pay_cycle(d)
        w *= DAY_WEIGHTS.get(pay_day, 1.0)

        date_weights.append(w)

    # Pick a date based on defined weights (weekend and payday bias)
    date = random.choices(all_dates, weights=date_weights, k=1)[0]

    # Pick an hour based on defined weights (evening bias)
    r = random.random()
    cumulative_weight = 0.0
    hour = 12  # Default fallback
    total_weight = sum(weight for _, (_, _, weight) in HOUR_WEIGHTS.items())

    for _, (hour_start, hour_end, weight) in HOUR_WEIGHTS.items():
        # Normalize weights
        cumulative_weight += weight / total_weight
        if r <= cumulative_weight:
            hour = random.randint(hour_start, hour_end - 1)
            break

    # Pick random minute and second
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    timestamp = datetime(date.year, date.month, date.day, hour, minute, second)
    return timestamp


def generate_scroll_depth(mission_choice):
    """
    Simulates scroll depth based on user intent.

    Behaviour:
    - Exploratory missoins -> deeper scroll
    - Purchase driven missions -> shallower scroll

    Used to influence time spent on page and engagement level.
    """
    base = (random.random() ** MISSION_SCROLL_BIAS.get(mission_choice, 1.0)) * 100

    # Assign scroll depth based on base value
    if base < 15:
        return random.randint(0, 15)

    elif base < 30:
        return random.choices([20, 25, 30], weights=[0.3, 0.4, 0.3], k=1)[0]

    elif base < 50:
        return random.choices([40, 50], weights=[0.4, 0.6], k=1)[0]

    elif base < 75:
        return random.choices([60, 75], weights=[0.5, 0.5], k=1)[0]

    else:
        return random.choices([85, 90, 100], weights=[0.3, 0.3, 0.4], k=1)[0]


############################
# SESSION ACTIVITY FUNCTIONS
############################


def determine_purchase_alpha_beta(mission_choice, has_treatment, customer_segment):
    """
    Generates Beta distribution parameters for purchase ratio.

    Factors:
    - Mission type
    - Campaign exposure
    - Customer segment
    """
    # Base parameters for different missions
    if mission_choice == "Bulk Buy":
        base_alpha, base_beta = 8, 2  # High purchase intent (mean ~0.8)
    elif mission_choice == "Regular Buy":
        base_alpha, base_beta = 6, 2  # Balanced intent (mean ~0.75)
    else:  # Quick Top Up or Browsing
        base_alpha, base_beta = 5, 2  # Lower purchase intent(mean ~0.71)

    # Increase purchase intent for treatment group

    if has_treatment:
        base_alpha *= 1.2

    # Adjust parameters based on customer segment
    if customer_segment == "High Spenders":
        base_alpha *= 1.1
        base_beta *= 0.9
    elif customer_segment == "Budget Shoppers":
        base_alpha *= 0.9
        base_beta *= 1.1
    elif customer_segment == "Churn Risk Customers":
        base_alpha *= 0.8
        base_beta *= 1.2

    # Ensure parameters are positive
    return max(base_alpha, 0.1), max(base_beta, 0.1)


def generate_activity_multiplier():
    """
    Generates user activity level using a Pareto distribution.

    Behaviour:
    - Many low activity users
    - Few high activity users

    Controls engagement intensity.
    """
    value = np.random.pareto(PARETO_ALPHA) + 1
    value = int(np.clip(value, 1, MAX_ACTIVITY_MULTIPLIER))
    return value


def decide_next_activity(
    ctx,
    activity_multiplier,
    customer_id,
    current_time,
    last_active_time,
    signup_date,
    customer_segment,
    cart_content,
):
    """
    Determines whether the user:
    - Continues (next session soon)
    - Becomes inactive
    - Churns

    Factors:
    - Customer Segment
    - Lifecycle stage
    - Recency
    - Cart State
    - Campaign exposure
    - Payday effects
    """
    base_return_prob = RETURN_PROB_BY_SEGMENT.get(customer_segment, 0.6)

    # Lifecycle effect
    days_since_signup = (current_time - signup_date).days
    if days_since_signup < 7:
        # Onboarding phrase (high engagement)
        lifecycle = 1.4
    elif days_since_signup < 30:
        # Settling phase
        lifecycle = 1.1
    elif days_since_signup < 180:
        # Habit phase (stable but lower)
        lifecycle = 0.9
    else:
        # Long term retention (low but non zero)
        lifecycle = 0.7

    # Recency effect
    days_since_last_active = (current_time - last_active_time).days
    if days_since_last_active <= 1:
        # Strong habit
        recency = 1.3
    elif days_since_last_active <= 7:
        recency = 1.1
    elif days_since_last_active <= 30:
        recency = 0.9
    elif days_since_last_active <= 90:
        recency = 0.7
    else:
        # Drifting
        recency = 0.5

    # Cart intent
    cart_boost = 1.0 + min(len(cart_content) * 0.1, 0.5)

    # Scale return probability if customer is under active campaign
    active_campaigns = get_active_campaigns(ctx, customer_id, current_time)

    if active_campaigns is None:
        campaign_boost = 1.0
    else:
        groups = set(active_campaigns["group"])
        if "Treatment" in groups:
            campaign_boost = 1.3
        elif "Control" in groups:
            campaign_boost = 1.1
        else:
            campaign_boost = 1.0

    # Scale return by payday
    pay_day = get_pay_cycle(current_time)
    if pay_day == "Payday":
        payday = 1.4
    elif pay_day == "Payday Spillover":
        payday = 1.15
    else:
        payday = 1.0

    # Base return probability adjusted by lifecycle, recency, cart state, campaign exposure and payday effects
    return_prob = (
        base_return_prob * lifecycle * recency * cart_boost * campaign_boost * payday
    )
    return_prob *= 0.7 + 0.3 * np.log1p(activity_multiplier)
    return_prob = min(return_prob, 0.99)

    # Base churn probability
    if days_since_last_active < 14:
        churn_base = 0.01
    elif days_since_last_active < 60:
        churn_base = 0.05
    else:
        churn_base = 0.15

    # Adjust churn by engagement & recency
    activity_factor = 1 / (1 + 0.3 * activity_multiplier)
    recency_factor = 1 / (1 + 0.5 * recency)
    churn_prob = churn_base * activity_factor * recency_factor

    # Compute inactive probability safely
    inactive_prob = max(0, 1 - return_prob - churn_prob)

    r = random.random()

    if r < return_prob:
        return "Continue"
    elif r < return_prob + inactive_prob:
        return "Inactive"
    else:
        return "Churn"


def sample_session_gap(
    customer_segment, cart_content, activity_multiplier, current_time, last_active_time
):
    """
    Samples time gap between active sessions

    Behaviour:
    - Mix of short, weekly, and longer return patterns
    - Adjusted by segment, cart state, and activity level
    """
    # Base gap drawn from customer segment
    base_gap = SESSION_GAP_SCALE_BY_SEGMENT.get(customer_segment, 24)

    cart_factor = 0.7 if cart_content else 1.0

    # Gap drawn from recency
    days_since_last_active = (current_time - last_active_time).days
    recency_factor = 1 + (days_since_last_active / 30)

    r = random.random()

    if r < 0.7:
        # Short term returns
        gap = np.random.exponential(scale=base_gap)
    elif r < 0.9:
        # Weekly pattern
        gap = np.random.lognormal(mean=3.0, sigma=0.5)
    else:
        # Occasional longer gap
        gap = np.random.lognormal(mean=5.0, sigma=0.7)

    gap = gap * cart_factor * recency_factor / activity_multiplier

    # Cap gap at 2 months to avoid extreme inactivity within simulation window
    return min(gap, 24 * 60)


def sample_inactive_gap(customer_segment):
    """
    Samples long inactivity periods (weeks to months).
    """
    if customer_segment == "High Spenders":
        # Shorter gaps
        return int(np.random.lognormal(mean=2.5, sigma=0.4))

    elif customer_segment == "Active Customers":
        return int(np.random.lognormal(mean=3.0, sigma=0.5))

    elif customer_segment == "Budget Shoppers":
        return int(np.random.lognormal(mean=3.2, sigma=0.6))

    elif customer_segment == "Churn Risk Customers":
        # Longer gaps
        return int(np.random.lognormal(mean=4.2, sigma=0.7))

    else:  # New Customer
        return int(np.random.lognormal(mean=2.8, sigma=0.5))


def compute_campaign_timing_boost(active_campaigns, current_time):
    """
    Computes boost to return probability based on campaign timing.
    """
    if active_campaigns is None:
        return 1.0

    boosts = []

    for _, row in active_campaigns.iterrows():
        start = row["start_date"]
        end = row["end_date"]

        total_days = (end - start).days
        if total_days <= 0:
            continue

        progress = (current_time - start).days / total_days

        if progress < 0.2:
            boost = 1.3  # Early engagement boost
        elif progress < 0.8:
            boost = 1.5  # Peak engagement boost
        else:
            boost = 0.8  # Fatigue effect towards end of campaign

        boosts.append(boost)

    return max(boosts) if boosts else 1.0


def attempt_reactivation(
    ctx,
    activity_multiplier,
    customer_id,
    current_time,
    last_active_time,
    customer_segment,
    cart_content,
):
    """
    Models return after inactivity.

    Determines:
    - Whether the user returns
    - When they return

    Drivers:
    - Campaign exposure (strongest)
    - Seasonal events
    - CRM nudges
    - Cart state
    - Payday effects
    """

    days_since_last_active = (current_time - last_active_time).days

    # Base probability by segment
    base_prob = REACTIVATION_BY_SEGMENT.get(customer_segment, 0.05)

    # Peak at ~30 days
    inactivity_factor = 1 + 0.8 * np.exp(
        -((days_since_last_active - 30) ** 2) / (2 * 20**2)
    )

    # Residual intent signals
    cart_boost = 1.1 + min(len(cart_content) * 0.05, 0.3)

    # Check if theres active campaign in new current time
    active_campaigns = get_active_campaigns(ctx, customer_id, current_time)

    # --- Campaign Reactivation ---
    if active_campaigns is None:
        campaign_boost = 1.0
    else:
        groups = set(active_campaigns["group"])
        if "Treatment" in groups:
            campaign_boost = 1.8
        elif "Control" in groups:
            campaign_boost = 1.2
        else:
            campaign_boost = 1.0

    # --- Campaign Timing Effect ---
    # Stronger boost at start and mid campaign, weaker towards end
    campaign_timing_boost = compute_campaign_timing_boost(
        active_campaigns, current_time
    )

    # --- Seasonal Reactivation ---
    season, season_type = get_seasonal_event(current_time)

    if season in SEASONAL_REACTIVATION_BOOST:
        seasonality_boost = SEASONAL_REACTIVATION_BOOST[season]
    elif season_type == "Commercial Mega Sale":
        seasonality_boost = 2.0  # Fallback
    elif season_type == "Cultural Festival":
        seasonality_boost = 1.3  # Fallback
    else:
        seasonality_boost = 1.0

    # --- Payday Reactivation ---
    pay_day = get_pay_cycle(current_time)
    if pay_day == "Payday":
        payday = 1.25
    elif pay_day == "Payday Spillover":
        payday = 1.1
    else:
        payday = 1.0
    payday *= 1.3

    # --- CRM Nudges ---
    if days_since_last_active < 7:
        nudge_boost = 1.1
    elif days_since_last_active < 30:
        nudge_boost = 1.4
    else:
        nudge_boost = 1.8

    # --- Final Reactivation Probability ---
    logit = np.log(base_prob / (1 - base_prob))

    logit += np.log(inactivity_factor)
    logit += np.log(cart_boost)
    logit += np.log(campaign_boost)
    logit += np.log(campaign_timing_boost)
    logit += np.log(seasonality_boost)
    logit += np.log(payday)
    logit += np.log(nudge_boost)

    logit += 0.3 * np.log1p(activity_multiplier)

    reactivation_prob = 1 / (1 + np.exp(-logit))
    reactivation_prob = min(reactivation_prob, 0.85)

    # Stronger boost for users who have been inactive for a long time
    if days_since_last_active > 60:
        reactivation_prob = max(reactivation_prob, 0.15)
    else:
        reactivation_prob = max(reactivation_prob, 0.08)

    # Decide WHETHER user returns
    if random.random() > reactivation_prob:
        # Stays inactive
        return None

    # Decide WHEN user returns
    base_days = np.random.lognormal(mean=3.2, sigma=0.5)

    if cart_content:
        base_days *= 0.7

    if season:
        base_days *= 0.8

    has_treatment = (
        active_campaigns is not None
        and (active_campaigns["group"] == "Treatment").any()
    )

    if has_treatment:
        base_days *= 0.6

    if pay_day == "Payday":
        base_days *= 0.75

    # --- Campaign Urgency ---
    if active_campaigns is not None:
        days_left_list = [
            (row["end_date"] - current_time).days
            for _, row in active_campaigns.iterrows()
        ]

        days_left = min(days_left_list)

        urgency = max(0.5, days_left / 7)
        base_days *= urgency

    return_in_days = int(np.clip(base_days, 1, 30))

    return current_time + timedelta(days=return_in_days)
