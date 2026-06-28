import random

import pandas as pd

from data_generation.config.clickstreams_config import (
    MAX_ACTIVITY_MULTIPLIER,
    MISSION_SCROLL_BIAS,
)
from data_generation.config.constants import (
    DATA_END_DATE,
    DATA_START_DATE,
)
from data_generation.services.clickstreams.clickstream_session_service import (
    compute_campaign_timing_boost,
    determine_purchase_alpha_beta,
    generate_activity_multiplier,
    generate_scroll_depth,
    generate_timestamp,
    sample_inactive_gap,
    sample_session_gap,
)
from tests.helpers import (
    _build_customer_segment,
    _build_datetime,
)

# ============================================================
# generate_timestamp()
# ============================================================


def test_clickstream_session_functions_generate_timestamp_within_range(N=20):
    """
    Generated timestamp must fall within the
    configured DATA_START_DATE / DATA_END_DATE window.
    """
    start = pd.Timestamp(DATA_START_DATE)
    end = pd.Timestamp(DATA_END_DATE) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    for _ in range(N):
        ts = generate_timestamp(start, end)
        assert pd.Timestamp(ts) >= start
        assert pd.Timestamp(ts) <= end
        assert 0 <= ts.hour < 24


def test_clickstream_session_functions_generate_timestamp_respects_narrow_window():
    """
    When the window is a single day, the
    timestamp must fall on that day.
    """
    day = pd.Timestamp(DATA_START_DATE)
    ts = generate_timestamp(day, day)
    assert pd.Timestamp(ts).date() == day.date()


# ============================================================
# generate_scroll_depth()
# ============================================================


def test_clickstream_session_functions_generate_scroll_depth(seed: int = 42):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    result = generate_scroll_depth(mission_choice)
    assert 0 <= result <= 100


def test_clickstream_session_functions_generate_scroll_depth_browsing_scrolls_deeper_than_quick_top_up(
    N=500,
):
    browsing = [generate_scroll_depth("Browsing") for _ in range(N)]
    quick = [generate_scroll_depth("Quick Top Up") for _ in range(N)]
    assert sum(browsing) / N > sum(quick) / N


# ============================================================
# determine_purchase_alpha_beta()
# ============================================================


def test_clickstream_session_functions_determine_purchase_alpha_beta(seed: int = 42):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    has_treatment = rng.choice([True, False])
    customer_segment = _build_customer_segment()
    alpha, beta = determine_purchase_alpha_beta(
        mission_choice, has_treatment, customer_segment
    )
    assert alpha >= 0.1
    assert beta >= 0.1


def test_clickstream_session_functions_determine_purchase_alpha_beta_mission_intent_ordering(
    seed: int = 42,
):
    rng = random.Random(seed)
    has_treatment = rng.choice([True, False])
    customer_segment = _build_customer_segment()
    a1, _ = determine_purchase_alpha_beta("Bulk Buy", has_treatment, customer_segment)
    a2, _ = determine_purchase_alpha_beta(
        "Regular Buy", has_treatment, customer_segment
    )
    a3, _ = determine_purchase_alpha_beta("Browsing", has_treatment, customer_segment)
    assert a1 > a2 > a3


def test_clickstream_session_functions_determine_purchase_alpha_beta_treatment_increases_alpha(
    seed: int = 42,
):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    customer_segment = _build_customer_segment()
    a1, b1 = determine_purchase_alpha_beta(mission_choice, False, customer_segment)
    a2, b2 = determine_purchase_alpha_beta(mission_choice, True, customer_segment)
    assert a2 > a1
    assert b2 == b1


def test_clickstream_session_functions_determine_purchase_alpha_beta_high_spender_segment_effect(
    seed: int = 42,
):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    has_treatment = rng.choice([True, False])
    a1, b1 = determine_purchase_alpha_beta(
        mission_choice, has_treatment, "Active Customers"
    )
    a2, b2 = determine_purchase_alpha_beta(
        mission_choice, has_treatment, "High Spenders"
    )
    assert a2 > a1
    assert b2 < b1


# ============================================================
# generate_activity_multiplier()
# ============================================================


def test_clickstream_session_functions_generate_activity_multiplier():
    result = generate_activity_multiplier()
    assert isinstance(result, int)
    assert 1 <= result <= MAX_ACTIVITY_MULTIPLIER


def test_clickstream_session_functions_generate_activity_multiplier_majority_are_low_activity_pareto(
    N=2000,
):
    result = [generate_activity_multiplier() for _ in range(N)]
    assert sum(r <= 2 for r in result) / N > 0.5


# ============================================================
# sample_session_gap()
# ============================================================


def test_clickstream_session_functions_sample_session_gap_is_positive_with_limit():
    """
    Gap between sessions must always be positive.
    """
    current_time = pd.Timestamp(DATA_START_DATE) + pd.Timedelta(days=30)
    last_active = current_time - pd.Timedelta(hours=5)

    customer_segment = _build_customer_segment()
    gap = sample_session_gap(
        customer_segment=customer_segment,
        cart_content=[],
        activity_multiplier=1,
        current_time=current_time,
        last_active_time=last_active,
    )

    assert gap > 0, f"Got non positive session gap {gap} "
    assert gap <= 24 * 60, "Gap should be capped at two months"


def test_clickstream_session_functions_sample_session_gap_cart_content_reduces_gap(
    N=1000,
):
    """
    A customer with items in their cart should
    return sooner (smaller gap) than one with an empty cart.
    """
    current_time = pd.Timestamp(DATA_START_DATE) + pd.Timedelta(days=30)
    last_active = current_time - pd.Timedelta(hours=5)
    customer_segment = _build_customer_segment()

    gaps_empty = [
        sample_session_gap(
            customer_segment=customer_segment,
            cart_content=[],
            activity_multiplier=1,
            current_time=current_time,
            last_active_time=last_active,
        )
        for _ in range(N)
    ]

    gaps_cart = [
        sample_session_gap(
            customer_segment=customer_segment,
            cart_content=["PROD001", "PROD002"],
            activity_multiplier=1,
            current_time=current_time,
            last_active_time=last_active,
        )
        for _ in range(N)
    ]

    assert sum(gaps_cart) < sum(
        gaps_empty
    ), "Cart content should reduce session gap (urgency to return)"


# ============================================================
# sample_inactive_gap()
# ============================================================


def test_clickstream_session_functions_sample_inactive_gap():
    customer_segment = _build_customer_segment()
    result = sample_inactive_gap(customer_segment)
    assert isinstance(result, int)


def test_clickstream_session_functions_sample_inactive_gap_segment_ordering():
    samples = {
        "High Spenders": [],
        "Active Customers": [],
        "Budget Shoppers": [],
        "Churn Risk Customers": [],
    }

    for _ in range(2000):
        for seg in samples:
            samples[seg].append(sample_inactive_gap(seg))

    means = {k: sum(v) / len(v) for k, v in samples.items()}

    assert means["High Spenders"] < means["Active Customers"]
    assert means["Active Customers"] < means["Budget Shoppers"]
    assert means["Budget Shoppers"] < means["Churn Risk Customers"]


# ============================================================
# compute_campaign_timing_boost()
# ============================================================


def test_clickstream_session_functions_campaign_timing_boost_none():
    current_time = _build_datetime()
    result = compute_campaign_timing_boost(None, current_time)
    assert result == 1.0


def test_clickstream_session_functions_compute_campaign_timing_boost_empty():
    current_time = _build_datetime()
    result = compute_campaign_timing_boost(pd.DataFrame(), current_time)
    assert result == 1.0


def test_clickstream_session_functions_compute_campaign_timing_boost_early():
    """
    Progress < 0.2 → boost should be 1.3.
    """
    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-04-01")
    current_time = pd.Timestamp("2024-01-05")  # ~1% through campaign
    campaigns = pd.DataFrame([{"start_date": start, "end_date": end}])
    result = compute_campaign_timing_boost(campaigns, current_time)
    assert result == 1.3


def test_clickstream_session_functions_compute_campaign_timing_boost_peak():
    """
    Progress 0.2-0.8 → boost should be 1.5.
    """
    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-04-01")
    current_time = pd.Timestamp("2024-02-15")  # ~50% through campaign
    campaigns = pd.DataFrame([{"start_date": start, "end_date": end}])
    result = compute_campaign_timing_boost(campaigns, current_time)
    assert result == 1.5


def test_clickstream_session_functions_compute_campaign_timing_boost_late():
    """
    Progress > 0.8 → boost should be 0.8 (fatigue).
    """
    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-04-01")
    current_time = pd.Timestamp("2024-03-28")  # ~95% through campaign
    campaigns = pd.DataFrame([{"start_date": start, "end_date": end}])
    result = compute_campaign_timing_boost(campaigns, current_time)
    assert result == 0.8
