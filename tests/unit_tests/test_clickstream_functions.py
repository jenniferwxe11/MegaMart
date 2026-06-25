import copy
import random
from datetime import timedelta

import pandas as pd
import pytest

from data_generation.config.clickstreams_config import (
    MISSION_SCROLL_BIAS,
    PROMOTION_TYPE_MULTIPLIER,
    TIME_ON_PAGE,
    VALID_EVENT_TRANSITIONS,
)
from data_generation.config.constants import (
    DATA_END_DATE,
    DATA_START_DATE,
    SEASONAL_DATES,
)
from data_generation.config.products_config import CATEGORIES, CATEGORY_AFFINITY
from data_generation.config.store_products_config import ESSENTIAL_CATEGORIES
from data_generation.services.clickstreams.clickstream_event_service import (
    resolve_category_view,
    resolve_page,
    resolve_scroll_and_time,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_random_product_from_category,
    get_random_product_from_search_term,
    get_search_term,
    get_segment_category,
    slugify,
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
from data_generation.services.clickstreams.clickstream_transition_service import (
    apply_mission_bias,
    apply_promotion_uplift,
    apply_purchase_progress_bias,
    apply_seasonal_uplift,
    apply_stock_status_uplift,
    get_base_transition_probability,
    normalise_probability,
    promotion_engagement_probability,
    promotion_perception_accuracy,
)
from tests.helpers import (
    _build_category,
    _build_customer_segment,
    _build_datetime,
)

# ============================================================
# resolve_scroll_and_time()
# ============================================================


def test_clickstream_resolve_scroll_and_time_browsing_event(seed: int = 42):
    rng = random.Random(seed)
    event_type = rng.choice(
        ["Home View", "Search View", "Category View", "Product View"]
    )
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    scroll, time = resolve_scroll_and_time(event_type, mission_choice)

    assert scroll is not None
    assert 0 <= scroll <= 100
    assert time > 0


def test_clickstream_resolve_scroll_and_time_non_browsing_event(seed: int = 42):
    rng = random.Random(seed)
    non_browsing_events = [
        e
        for e in TIME_ON_PAGE.keys()
        if e not in ("Home View", "Search View", "Category View", "Product View")
    ]
    event_type = rng.choice(non_browsing_events)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    scroll, time = resolve_scroll_and_time(event_type, mission_choice)

    assert scroll is None
    assert time > 0


def test_clickstream_resolve_scroll_and_time_compare_time(seed: int = 42):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    browsing_times = []
    non_browsing_times = []
    for _ in range(100):
        _, t1 = resolve_scroll_and_time("Home View", mission_choice)
        _, t2 = resolve_scroll_and_time("Payment Attempt", mission_choice)
        browsing_times.append(t1)
        non_browsing_times.append(t2)

    assert sum(browsing_times) > sum(non_browsing_times)


# ============================================================
# resolve_page()
# ============================================================


def test_clickstream_resolve_page_static_routes():
    assert resolve_page("Home View", None, None, None) == "/home"
    assert resolve_page("Cart View", None, None, None) == "/cart"
    assert resolve_page("Checkout Start", None, None, None) == "/checkout"


def test_clickstream_resolve_page_product_routes():
    product_id = "PROD001"

    assert resolve_page("Product View", product_id, None, None) == "/product/PROD001"
    assert resolve_page("Add to Cart", product_id, None, None) == "/add_to_cart/PROD001"
    assert (
        resolve_page("Remove from Cart", product_id, None, None)
        == "/remove_from_cart/PROD001"
    )


def test_clickstream_resolve_page_category_route():
    result = resolve_page("Category View", None, "Electronics & Appliances", None)
    assert result == "/category/electronics-and-appliances"


def test_clickstream_resolve_page_search_route():
    result = resolve_page("Search View", None, None, "laptop")
    assert result == "/search?q=laptop"


def test_clickstream_resolve_page_priority_product_over_category():
    result = resolve_page(
        "Product View", "PROD001", "Electronics & Appliances", "laptop"
    )
    assert result == "/product/PROD001"


def test_clickstream_resolve_page_priority_category_over_search():
    result = resolve_page("Category View", None, "Electronics & Appliances", "laptop")
    assert result == "/category/electronics-and-appliances"


# ============================================================
# resolve_category_view()
# ============================================================


def test_clickstream_session_flow_resolve_category_view_returns_valid_category():
    """
    Integration contract: resolve_category_view() must return a string
    that matches one of the known product categories.
    """
    customer_segment = _build_customer_segment()
    for _ in range(20):
        cat = resolve_category_view(
            previous_category=None,
            customer_segment=customer_segment,
            session_affinity_categories=set(),
        )
        assert (
            cat in CATEGORIES
        ), f"resolve_category_view() returned unknown category {cat!r}"


def test_clickstream_session_flow_resolve_category_view_affinity_category_bias_with_previous_category():
    """
    Integration contract: when a previous_category with known affinity
    relationships exists, the returned category should frequently be
    within the affinity cluster (~70% of the time).
    """
    # Find a category that has affinity relationships
    seeded_category = None
    affinity_set = set()
    for cat, affinities in CATEGORY_AFFINITY.items():
        if affinities:
            seeded_category = cat
            affinity_set = {cat} | set(affinities)
            break

    if seeded_category is None:
        pytest.skip("No categories with affinity relationships in config")

    customer_segment = _build_customer_segment()

    hits = sum(
        1
        for _ in range(100)
        if resolve_category_view(
            previous_category=seeded_category,
            customer_segment=customer_segment,
            session_affinity_categories=affinity_set,
        )
        in affinity_set
    )
    assert hits >= 55, (
        f"Expected affinity category hit rate >= 55%, got {hits}% "
        f"for seeded category {seeded_category!r}"
    )


def test_clickstream_session_flow_resolve_category_view_no_previous_category_still_returns_valid_category():
    """
    Integration contract: with no prior browsing context the function
    must still return a valid category (segment-based fallback).
    """
    customer_segment = _build_customer_segment()
    cat = resolve_category_view(
        previous_category=None,
        customer_segment=customer_segment,
        session_affinity_categories=set(),
    )
    assert cat in CATEGORIES, (
        f"resolve_category_view() returned unknown category {cat!r} "
        f"for segment {customer_segment!r}"
    )


# ============================================================
# get_search_term()
# ============================================================
# UNIT: only reads ctx.reference_data.search_terms — a static list,
# not a generated DataFrame.


def test_clickstream_get_search_term(ctx):
    result = get_search_term(ctx)
    assert isinstance(result, str)
    assert "&" not in result
    assert " " not in result


# ============================================================
# slugify()
# ============================================================


def test_clickstream_slugify_space():
    assert slugify("Hello World") == "hello-world"


def test_clickstream_slugify_ampersand_replaced():
    assert slugify("A & B") == "a-and-b"


def test_clickstream_slugify_removes_punctuation():
    assert slugify("Python, Rocks!") == "python-rocks"


def test_clickstream_slugify_multiple_spaces():
    assert slugify("Hello    World") == "hello-world"


def test_clickstream_slugify_empty_string():
    assert slugify("") == ""


# ============================================================
# generate_timestamp()
# ============================================================


def test_clickstream_generate_timestamp_within_range():
    """
    Generated timestamp must fall within the
    configured DATA_START_DATE / DATA_END_DATE window.
    """
    start = pd.Timestamp(DATA_START_DATE)
    end = pd.Timestamp(DATA_END_DATE)

    for _ in range(20):
        ts = generate_timestamp(start, end)
        assert pd.Timestamp(ts) >= start
        assert pd.Timestamp(ts) <= end


def test_timestamp_respects_narrow_window():
    """
    When the window is a single day, the
    timestamp must fall on that day.
    """
    day = pd.Timestamp(DATA_START_DATE)
    ts = generate_timestamp(day, day)
    assert pd.Timestamp(ts).date() == day.date()


# ============================================================
# get_random_product_from_search_term()
# ============================================================
# UNIT: reads ctx.products.products_df (via product_ctx).
# The logic under test is string matching — not cross table joins.


def test_clickstream_get_random_product_from_search_term(product_ctx, seed: int = 42):
    # Simulate user search term using product
    df = product_ctx.products.products_df
    row = df.sample(n=1, random_state=seed).iloc[0]
    product_name = row["product_name"]
    search_term = product_name.split()[0]

    result = get_random_product_from_search_term(product_ctx, search_term)

    # Validate all returned products actually match search logic
    assert result is None or isinstance(result, list)
    if result:
        for pid in result:
            matched_name = df.loc[df["product_id"] == pid, "product_name"].iloc[0]
            assert search_term.replace("+", " ").lower() in matched_name.lower()


# ============================================================
# get_segment_category()
# ============================================================


def test_clickstream_get_segment_category():
    customer_segment = _build_customer_segment()
    result = get_segment_category(customer_segment)
    assert isinstance(result, str)
    assert result in CATEGORIES


# ============================================================
# get_random_product_from_category()
# ============================================================
# UNIT: reads ctx.products.category_to_products (built from products_df).
# The logic is a dict lookup + random choice — no multi table wiring.


def test_clickstream_get_random_product_from_category(product_ctx, seed: int = 42):
    random.seed(seed)
    (category,) = _build_category(product_ctx, 1)
    result = get_random_product_from_category(product_ctx, category)
    assert result in product_ctx.products.category_to_products[category]


def test_clickstream_get_random_product_from_category_empty(product_ctx):
    category = "NON_EXISTENT_CATEGORY"
    result = get_random_product_from_category(product_ctx, category)
    assert result is None


# ============================================================
# generate_scroll_depth()
# ============================================================


def test_clickstream_generate_scroll_depth(seed: int = 42):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    result = generate_scroll_depth(mission_choice)
    assert 0 <= result <= 100


# ============================================================
# determine_purchase_alpha_beta()
# ============================================================


def test_clickstream_determine_purchase_alpha_beta(seed: int = 42):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    has_treatment = rng.choice([True, False])
    customer_segment = _build_customer_segment()
    alpha, beta = determine_purchase_alpha_beta(
        mission_choice, has_treatment, customer_segment
    )
    assert alpha >= 0.1
    assert beta >= 0.1


def test_clickstream_determine_purchase_alpha_beta_mission_intent_ordering(
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


def test_clickstream_determine_purchase_alpha_beta_treatment_increases_alpha(
    seed: int = 42,
):
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    customer_segment = _build_customer_segment()
    a1, b1 = determine_purchase_alpha_beta(mission_choice, False, customer_segment)
    a2, b2 = determine_purchase_alpha_beta(mission_choice, True, customer_segment)
    assert a2 > a1
    assert b2 == b1


def test_clickstream_determine_purchase_alpha_beta_high_spender_segment_effect(
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


def test_clickstream_generate_activity_multiplier():
    result = generate_activity_multiplier()
    assert isinstance(result, int)


# ============================================================
# sample_session_gap()
# ============================================================


def test_clickstream_sample_session_gap_is_positive():
    """
    Gap between sessions must always be positive.
    """
    current_time = pd.Timestamp(DATA_START_DATE) + pd.Timedelta(days=30)
    last_active = current_time - pd.Timedelta(hours=5)

    customer_segment = _build_customer_segment()
    gap = sample_session_gap(
        customer_segment=customer_segment,
        cart_content=[],
        activity_multiplier=3,
        current_time=current_time,
        last_active_time=last_active,
    )

    assert gap > 0, f"Got non positive session gap {gap} "


def test_clickstream_sample_session_gap_cart_content_reduces_gap():
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
            activity_multiplier=3,
            current_time=current_time,
            last_active_time=last_active,
        )
        for _ in range(200)
    ]

    gaps_cart = [
        sample_session_gap(
            customer_segment=customer_segment,
            cart_content=["PROD001", "PROD002"],
            activity_multiplier=3,
            current_time=current_time,
            last_active_time=last_active,
        )
        for _ in range(200)
    ]

    assert sum(gaps_cart) < sum(
        gaps_empty
    ), "Cart content should reduce session gap (urgency to return)"


# ============================================================
# sample_inactive_gap()
# ============================================================


def test_clickstream_sample_inactive_gap():
    customer_segment = _build_customer_segment()
    result = sample_inactive_gap(customer_segment)
    assert isinstance(result, int)


def test_clickstream_sample_inactive_gap_segment_ordering():
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


def test_clickstream_campaign_timing_boost_none():
    current_time = _build_datetime()
    result = compute_campaign_timing_boost(None, current_time)
    assert result == 1.0


def test_clickstream_compute_campaign_timing_boost_empty():
    current_time = _build_datetime()
    result = compute_campaign_timing_boost(pd.DataFrame(), current_time)
    assert result == 1.0


def test_clickstream_compute_campaign_timing_boost_early():
    """
    Progress < 0.2 → boost should be 1.3.
    """
    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-04-01")
    current_time = pd.Timestamp("2024-01-05")  # ~1% through campaign
    campaigns = pd.DataFrame([{"start_date": start, "end_date": end}])
    result = compute_campaign_timing_boost(campaigns, current_time)
    assert result == 1.3


def test_clickstream_compute_campaign_timing_boost_peak():
    """
    Progress 0.2-0.8 → boost should be 1.5.
    """
    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-04-01")
    current_time = pd.Timestamp("2024-02-15")  # ~50% through campaign
    campaigns = pd.DataFrame([{"start_date": start, "end_date": end}])
    result = compute_campaign_timing_boost(campaigns, current_time)
    assert result == 1.5


def test_clickstream_compute_campaign_timing_boost_late():
    """
    Progress > 0.8 → boost should be 0.8 (fatigue).
    """
    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2024-04-01")
    current_time = pd.Timestamp("2024-03-28")  # ~95% through campaign
    campaigns = pd.DataFrame([{"start_date": start, "end_date": end}])
    result = compute_campaign_timing_boost(campaigns, current_time)
    assert result == 0.8


# ============================================================
# apply_seasonal_uplift()
# ============================================================


def _base_transition_probability():
    return {
        "Product View": {
            "Add to Cart": 1.0,
            "Search View": 1.0,
            "Cart View": 1.0,
        },
        "Category View": {
            "Product View": 1.0,
        },
        "Cart View": {
            "Checkout Start": 1.0,
            "Product View": 1.0,
        },
        "Checkout Start": {
            "Payment Attempt": 1.0,
        },
    }


def test_clickstream_apply_seasonal_uplift_season_increases_target_transitions():
    transition_probability = _base_transition_probability()

    season = pd.Timestamp(SEASONAL_DATES["Commercial Mega Sale"]["Black Friday"][0])

    result = apply_seasonal_uplift(
        timestamp=season,
        transition_probability=transition_probability,
        progress=0.5,
    )

    assert result["Product View"]["Add to Cart"] > 1.0
    assert result["Cart View"]["Checkout Start"] > 1.0
    assert result["Checkout Start"]["Payment Attempt"] > 1.0


def test_clickstream_apply_seasonal_uplift_evening_increases_target_transitions():
    transition_probability = _base_transition_probability()
    dt = _build_datetime()
    evening = dt.replace(hour=18, minute=0, second=0, microsecond=0)

    result = apply_seasonal_uplift(
        timestamp=evening,
        transition_probability=transition_probability,
        progress=0.5,
    )

    assert result["Product View"]["Add to Cart"] > 1.0
    assert result["Cart View"]["Checkout Start"] > 1.0
    assert result["Checkout Start"]["Payment Attempt"] > 1.0


def test_clickstream_apply_seasonal_uplift_payday_increases_target_transitions():
    transition_probability = _base_transition_probability()
    dt = _build_datetime()
    payday = dt.replace(day=15)

    result = apply_seasonal_uplift(
        timestamp=payday,
        transition_probability=transition_probability,
        progress=0.5,
    )

    assert result["Product View"]["Add to Cart"] > 1.0
    assert result["Cart View"]["Checkout Start"] > 1.0
    assert result["Checkout Start"]["Payment Attempt"] > 1.0


def test_clickstream_apply_seasonal_uplift_weekend_increases_target_transitions():
    transition_probability = _base_transition_probability()
    dt = _build_datetime()
    # Move to next Saturday
    weekend = dt + timedelta(days=(5 - dt.weekday()) % 7)

    result = apply_seasonal_uplift(
        timestamp=weekend,
        transition_probability=transition_probability,
        progress=0.5,
    )

    assert result["Product View"]["Add to Cart"] > 1.0
    assert result["Cart View"]["Checkout Start"] > 1.0
    assert result["Checkout Start"]["Payment Attempt"] > 1.0


# ============================================================
# promotion_engagement_probability()
# ============================================================


def test_clickstream_promotion_engagement_probability_relevant_scope_higher_than_irrelevant():
    promo = {
        "promotion_scope": "cart",
        "promotion_mechanic": "percentage_discount",
        "promotion_value": 20,
    }

    relevant = promotion_engagement_probability(
        promo=promo,
        event_type="Cart View",
        times_seen=1,
    )

    irrelevant = promotion_engagement_probability(
        promo=promo,
        event_type="Product View",
        times_seen=1,
    )

    assert relevant > irrelevant


def test_clickstream_promotion_engagement_probability_bundle_cap_at_10():
    promo = {
        "promotion_scope": "bundle",
        "promotion_mechanic": "bundle",
        "promotion_value": 50,
    }

    result = promotion_engagement_probability(
        promo=promo,
        event_type="Product View",
        times_seen=1,
    )

    assert result <= 10


def test_clickstream_promotion_engagement_probability_dollar_discount_cap_at_5():
    promo = {
        "promotion_scope": "product",
        "promotion_mechanic": "dollar_discount",
        "promotion_value": 20,
    }

    result = promotion_engagement_probability(
        promo=promo,
        event_type="Product View",
        times_seen=1,
    )

    assert result <= 5


def test_clickstream_promotion_engagement_probability_unknown_mechanic_handling():
    promo = {
        "promotion_scope": "product",
        "promotion_mechanic": "UNKNOWN_MECHANIC",
        "promotion_value": 100,
    }

    result = promotion_engagement_probability(
        promo=promo,
        event_type="Product View",
        times_seen=1,
    )

    assert 0 <= result <= 0.9


# ============================================================
# promotion_perception_accuracy()
# ============================================================


def test_clickstream_promotion_perception_accuracy():
    dollar = promotion_perception_accuracy({"promotion_mechanic": "dollar_discount"})
    percentage = promotion_perception_accuracy(
        {"promotion_mechanic": "percentage_discount"}
    )
    bundle = promotion_perception_accuracy({"promotion_mechanic": "bundle"})
    assert percentage > dollar > bundle


# ============================================================
# apply_promotion_uplift()
# ============================================================


def test_clickstream_apply_promotion_uplift_config_validity():
    for _, config in PROMOTION_TYPE_MULTIPLIER.items():
        assert config["atc_multiplier"][0] <= config["atc_multiplier"][1]
        assert config["checkout_multiplier"][0] <= config["checkout_multiplier"][1]
        assert config["remove_multiplier"][0] <= config["remove_multiplier"][1]


def test_clickstream_apply_promotion_uplift_free_shipping_effect():
    base_transition = copy.deepcopy(VALID_EVENT_TRANSITIONS)
    result = apply_promotion_uplift(
        transition_probability=base_transition,
        selected_promotions=[
            {"promotion_id": "PROMO001", "promotion_mechanic": "free_shipping"}
        ],
        seen_promotions={},
        seen_promo_types={},
        progress=0.9,
    )

    assert (
        result["Product View"]["Add to Cart"]
        > VALID_EVENT_TRANSITIONS["Product View"]["Add to Cart"]
    )
    assert (
        result["Cart View"]["Remove from Cart"]
        < VALID_EVENT_TRANSITIONS["Cart View"]["Remove from Cart"]
    )
    assert (
        result["Cart View"]["Checkout Start"]
        > VALID_EVENT_TRANSITIONS["Cart View"]["Checkout Start"]
    )


def test_clickstream_apply_promotion_uplift_discount_types_stronger_than_free_shipping():
    base_transition_free_shipping = copy.deepcopy(VALID_EVENT_TRANSITIONS)
    base_transition_percentage = copy.deepcopy(VALID_EVENT_TRANSITIONS)

    free = apply_promotion_uplift(
        transition_probability=base_transition_free_shipping,
        selected_promotions=[
            {"promotion_id": "PROMO001", "promotion_mechanic": "free_shipping"}
        ],
        seen_promotions={},
        seen_promo_types={},
        progress=0.5,
    )

    percent = apply_promotion_uplift(
        transition_probability=base_transition_percentage,
        selected_promotions=[
            {"promotion_id": "PROMO001", "promotion_mechanic": "percentage_discount"}
        ],
        seen_promotions={},
        seen_promo_types={},
        progress=0.5,
    )

    assert percent["Product View"]["Add to Cart"] > free["Product View"]["Add to Cart"]


def test_clickstream_apply_promotion_uplift_bundle_reduces_cart_removal():
    base_transition = copy.deepcopy(VALID_EVENT_TRANSITIONS)
    result = apply_promotion_uplift(
        transition_probability=base_transition,
        selected_promotions=[
            {"promotion_id": "PROMO001", "promotion_mechanic": "bundle"}
        ],
        seen_promotions={},
        seen_promo_types={},
        progress=0.5,
    )

    assert (
        result["Cart View"]["Remove from Cart"]
        < VALID_EVENT_TRANSITIONS["Cart View"]["Remove from Cart"]
    )


def test_clickstream_apply_promotion_uplift_multiple_promotions_increase_uplift():
    base_transition_single = copy.deepcopy(VALID_EVENT_TRANSITIONS)
    base_transition_stacked = copy.deepcopy(VALID_EVENT_TRANSITIONS)

    single = apply_promotion_uplift(
        transition_probability=base_transition_single,
        selected_promotions=[
            {"promotion_id": "PROMO001", "promotion_mechanic": "free_shipping"}
        ],
        seen_promotions={},
        seen_promo_types={},
        progress=0.5,
    )

    stacked = apply_promotion_uplift(
        transition_probability=base_transition_stacked,
        selected_promotions=[
            {"promotion_id": "PROMO001", "promotion_mechanic": "free_shipping"},
            {"promotion_id": "PROMO002", "promotion_mechanic": "free_shipping"},
        ],
        seen_promotions={},
        seen_promo_types={},
        progress=0.5,
    )

    assert (
        stacked["Product View"]["Add to Cart"] > single["Product View"]["Add to Cart"]
    )


# ============================================================
# apply_stock_status_uplift()
# ============================================================
# UNIT: monkeypatches get_product_stock_status so real stock data
# is never read. stock_snapshot_ctx is passed only because the
# function signature requires ctx — the patched function ignores it.


def test_clickstream_apply_stock_status_uplift_out_of_stock(
    stock_snapshot_ctx, monkeypatch
):
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_transition_service.get_product_stock_status",
        lambda *args, **kwargs: "Out of Stock",
    )

    transition_probability = {
        "Product View": {
            "Add to Cart": 1.0,
            "Home View": 1.0,
            "Category View": 1.0,
            "Search View": 1.0,
        }
    }

    result = apply_stock_status_uplift(
        stock_snapshot_ctx,
        transition_probability,
        store_id="STOR001",
        product_id="PROD001",
        timestamp=_build_datetime(),
    )

    assert "Add to Cart" not in result["Product View"]
    assert result["Product View"]["Home View"] == 1.2
    assert result["Product View"]["Category View"] == 1.3
    assert result["Product View"]["Search View"] == 1.2


def test_clickstream_apply_stock_status_uplift_low_stock(
    stock_snapshot_ctx, monkeypatch
):
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_transition_service.get_product_stock_status",
        lambda *args, **kwargs: "Low Stock",
    )

    transition_probability = {
        "Product View": {
            "Add to Cart": 1.0,
            "Home View": 1.0,
        }
    }

    result = apply_stock_status_uplift(
        stock_snapshot_ctx,
        transition_probability,
        store_id="STOR001",
        product_id="PROD001",
        timestamp=_build_datetime(),
    )

    assert result["Product View"]["Add to Cart"] == 1.2
    assert result["Product View"]["Home View"] == 1.0


def test_clickstream_apply_stock_status_uplift_in_stock(
    stock_snapshot_ctx, monkeypatch
):
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_transition_service.get_product_stock_status",
        lambda *args, **kwargs: "In Stock",
    )

    transition_probability = {
        "Product View": {
            "Add to Cart": 1.0,
        }
    }

    result = apply_stock_status_uplift(
        stock_snapshot_ctx,
        transition_probability,
        store_id="STOR001",
        product_id="PROD001",
        timestamp=_build_datetime(),
    )

    assert result["Product View"]["Add to Cart"] == 1.1


def test_clickstream_apply_stock_status_uplift_no_product_id(stock_snapshot_ctx):
    base = {
        "Product View": {
            "Add to Cart": 1.0,
        }
    }

    result = apply_stock_status_uplift(
        stock_snapshot_ctx,
        base,
        store_id="STOR001",
        product_id=None,
        timestamp=_build_datetime(),
    )

    assert result == base


# ============================================================
# get_base_transition_probability()
# ============================================================


@pytest.mark.parametrize(
    "customer_segment, has_treatment, expected",
    [
        (
            "High Spenders",
            False,
            {
                "Product View": {"Add to Cart": 1.1},
                "Cart View": {"Checkout Start": 1.1},
            },
        ),
        (
            "Budget Shoppers",
            False,
            {
                "Product View": {"Add to Cart": 0.9, "Search View": 1.1},
                "Cart View": {"Checkout Start": 0.9},
            },
        ),
        (
            "Churn Risk Customers",
            False,
            {
                "Product View": {"Add to Cart": 0.85},
                "Cart View": {"Checkout Start": 0.85},
            },
        ),
        (
            "High Spenders",
            True,
            {
                "Product View": {"Add to Cart": 1.1 * 1.1},
                "Cart View": {"Checkout Start": 1.1 * 1.1},
                "Checkout Start": {"Payment Attempt": 1.1},
            },
        ),
        (
            "Budget Shoppers",
            True,
            {
                "Product View": {
                    "Add to Cart": 0.9 * 1.1,
                    "Search View": 1.1,
                },
                "Cart View": {"Checkout Start": 0.9 * 1.1},
                "Checkout Start": {"Payment Attempt": 1.1},
            },
        ),
        (
            "Churn Risk Customers",
            True,
            {
                "Product View": {"Add to Cart": 0.85 * 1.1},
                "Cart View": {"Checkout Start": 0.85 * 1.1},
                "Checkout Start": {"Payment Attempt": 1.1},
            },
        ),
    ],
)
def test_clickstream_get_base_transition_probability(
    customer_segment, has_treatment, expected
):
    transition_probability = _base_transition_probability()
    result = get_base_transition_probability(
        transition_probability=transition_probability,
        customer_segment=customer_segment,
        has_treatment=has_treatment,
    )

    for event, transitions in expected.items():
        for key, value in transitions.items():
            assert result[event][key] == value


# ============================================================
# apply_mission_bias()
# ============================================================


def test_clickstream_apply_mission_bias_no_previous_event_type(seed: int = 42):
    transition_probability = _base_transition_probability()
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    result = apply_mission_bias(
        event_transition_probability=transition_probability,
        mission_choice=mission_choice,
        previous_event_type=None,
        progress=0.5,
    )

    assert result == transition_probability


def test_clickstream_apply_mission_bias_unknown_mission():
    transition_probability = _base_transition_probability()
    result = apply_mission_bias(
        event_transition_probability=transition_probability,
        mission_choice="UNKNOWN_MISSION",
        previous_event_type="Product View",
        progress=0.5,
    )

    assert result == transition_probability


def test_clickstream_apply_mission_bias_previous_event_not_found(seed: int = 42):
    transition_probability = _base_transition_probability()
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    result = apply_mission_bias(
        event_transition_probability=transition_probability,
        mission_choice=mission_choice,
        previous_event_type="Home View",
        progress=0.5,
    )

    assert result == transition_probability


def test_clickstream_apply_mission_bias_applies_multiplier(seed: int = 42):
    transition_probability = _base_transition_probability()
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    result = apply_mission_bias(
        event_transition_probability=transition_probability,
        mission_choice=mission_choice,
        previous_event_type="Product View",
        progress=0.5,
    )

    assert result["Product View"]["Add to Cart"] > 1.0


def test_clickstream_apply_mission_bias_checkout_progress_scaling(seed: int = 42):
    low_process_transition_probability = _base_transition_probability()
    high_process_transition_probability = _base_transition_probability()
    rng = random.Random(seed)
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))

    low_result = apply_mission_bias(
        event_transition_probability=low_process_transition_probability,
        mission_choice=mission_choice,
        previous_event_type="Cart View",
        progress=0.0,
    )

    high_result = apply_mission_bias(
        event_transition_probability=high_process_transition_probability,
        mission_choice=mission_choice,
        previous_event_type="Cart View",
        progress=1.0,
    )

    assert (
        high_result["Cart View"]["Checkout Start"]
        >= low_result["Cart View"]["Checkout Start"]
    )


# ============================================================
# apply_purchase_progress_bias()
# ============================================================


def test_clickstream_apply_purchase_progress_bias_missing_previous_event():
    base = _base_transition_probability()
    result = apply_purchase_progress_bias(
        base,
        previous_event_type=None,
        previous_category=None,
        events=[],
        progress=0.3,
    )

    assert result == base


def test_clickstream_apply_purchase_progress_bias_early_stage_add_to_cart_streak_encourage_browsing():
    base = _base_transition_probability()
    previous_event_type = "Product View"
    result = apply_purchase_progress_bias(
        base,
        previous_event_type,
        previous_category=None,
        events=["Add to Cart", "Add to Cart"],  # streak >= 2
        progress=0.3,
    )

    assert result[previous_event_type]["Add to Cart"] == 2.0
    assert result[previous_event_type]["Cart View"] == 0.85


def test_clickstream_apply_purchase_progress_bias_early_stage_add_to_cart_streak_discourage_checkout():
    base = _base_transition_probability()
    previous_event_type = "Cart View"
    result = apply_purchase_progress_bias(
        base,
        previous_event_type,
        previous_category=None,
        events=["Add to Cart", "Add to Cart"],  # streak >= 2
        progress=0.3,
    )

    assert result[previous_event_type]["Product View"] == 2.0
    assert result[previous_event_type]["Checkout Start"] == 0.3


def test_clickstream_apply_purchase_progress_bias_mid_stage():
    base = _base_transition_probability()
    previous_event_type = "Cart View"

    result = apply_purchase_progress_bias(
        base,
        previous_event_type,
        previous_category=None,
        events=[],
        progress=0.6,
    )

    assert result[previous_event_type]["Checkout Start"] == 0.5


def test_apply_purchase_progress_bias_late_stage():
    base = _base_transition_probability()
    previous_event_type = "Cart View"

    result = apply_purchase_progress_bias(
        base,
        previous_event_type,
        previous_category=None,
        events=[],
        progress=0.9,
    )

    assert result[previous_event_type]["Checkout Start"] == 2.0
    assert result[previous_event_type]["Product View"] == 0.6


def test_apply_purchase_progress_bias_essential_category_boost(seed: int = 42):
    rng = random.Random(seed)
    base = _base_transition_probability()
    previous_event_type = "Product View"
    previous_category = rng.choice(ESSENTIAL_CATEGORIES)

    result = apply_purchase_progress_bias(
        base,
        previous_event_type,
        previous_category,
        events=[],
        progress=0.3,
    )

    assert result[previous_event_type]["Add to Cart"] == 1.1


# ============================================================
# normalise_probability()
# ============================================================


def _unnormalised_base_transition_probability():
    return {
        "Product View": {
            "Add to Cart": 2.0,
            "Search View": 1.5,
            "Cart View": 0.85,
        },
        "Cart View": {
            "Checkout Start": 3.0,
            "Product View": 0.5,
        },
        "Search View": {
            "Product View": 1.5,
        },
        "Checkout Start": {
            "Payment Attempt": 0.0,
        },
    }


def test_clickstream_normalise_probability_basic_normalisation():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)
    pv = result["Product View"]

    assert pv["Add to Cart"] == 2.0 / (2.0 + 1.5 + 0.85)
    assert pv["Search View"] == 1.5 / (2.0 + 1.5 + 0.85)
    assert pv["Cart View"] == 0.85 / (2.0 + 1.5 + 0.85)
    assert abs(sum(pv.values()) - 1.0) < 1e-9


def test_clickstream_normalise_probability_preserves_ratios():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)
    pv = result["Product View"]

    ratio_original = 2.0 / 0.85
    ratio_normalized = pv["Add to Cart"] / pv["Cart View"]

    assert abs(ratio_original - ratio_normalized) < 1e-9


def test_clickstream_normalise_probability_zero_total_unchanged():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)
    pv = result["Checkout Start"]

    assert pv["Payment Attempt"] == 0.0


def test_clickstream_normalise_probability_independent_event_groups():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)

    pv_sum = sum(result["Product View"].values())
    cv_sum = sum(result["Cart View"].values())

    assert abs(pv_sum - 1.0) < 1e-9
    assert abs(cv_sum - 1.0) < 1e-9


def test_clickstream_normalise_probability_single_transition():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)

    assert result["Search View"]["Product View"] == 1.0
