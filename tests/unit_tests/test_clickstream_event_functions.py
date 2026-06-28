import random

import pytest

from data_generation.config.clickstreams_config import (
    MISSION_SCROLL_BIAS,
    TIME_ON_PAGE,
)
from data_generation.config.products_config import CATEGORIES, CATEGORY_AFFINITY
from data_generation.services.clickstreams.clickstream_event_service import (
    resolve_category_view,
    resolve_page,
    resolve_scroll_and_time,
)
from tests.helpers import _build_customer_segment

# ============================================================
# resolve_scroll_and_time()
# ============================================================


def test_clickstream_event_functions_resolve_scroll_and_time_browsing_event(
    seed: int = 42,
):
    rng = random.Random(seed)
    event_type = rng.choice(
        ["Home View", "Search View", "Category View", "Product View"]
    )
    mission_choice = rng.choice(list(MISSION_SCROLL_BIAS.keys()))
    scroll, time = resolve_scroll_and_time(event_type, mission_choice)

    assert scroll is not None
    assert 0 <= scroll <= 100
    assert time > 0


def test_clickstream_event_functions_resolve_scroll_and_time_non_browsing_event(
    seed: int = 42,
):
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


def test_clickstream_event_functions_resolve_scroll_and_time_compare_time(
    seed: int = 42,
):
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


def test_clickstream_event_functions_resolve_page_static_routes():
    assert resolve_page("Home View", None, None, None) == "/home"
    assert resolve_page("Cart View", None, None, None) == "/cart"
    assert resolve_page("Checkout Start", None, None, None) == "/checkout"


def test_clickstream_event_functions_resolve_page_product_routes():
    product_id = "PROD001"

    assert resolve_page("Product View", product_id, None, None) == "/product/PROD001"
    assert resolve_page("Add to Cart", product_id, None, None) == "/add_to_cart/PROD001"
    assert (
        resolve_page("Remove from Cart", product_id, None, None)
        == "/remove_from_cart/PROD001"
    )


def test_clickstream_event_functions_resolve_page_category_route():
    result = resolve_page("Category View", None, "Electronics & Appliances", None)
    assert result == "/category/electronics-and-appliances"


def test_clickstream_event_functions_resolve_page_search_route():
    result = resolve_page("Search View", None, None, "laptop")
    assert result == "/search?q=laptop"


def test_clickstream_event_functions_resolve_page_priority_product_over_category():
    result = resolve_page(
        "Product View", "PROD001", "Electronics & Appliances", "laptop"
    )
    assert result == "/product/PROD001"


def test_clickstream_event_functions_resolve_page_priority_category_over_search():
    result = resolve_page("Category View", None, "Electronics & Appliances", "laptop")
    assert result == "/category/electronics-and-appliances"


# ============================================================
# resolve_category_view()
# ============================================================


def test_clickstream_event_functions_resolve_category_view_returns_valid_category():
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


def test_clickstream_event_functions_resolve_category_view_affinity_category_bias_with_previous_category():
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


def test_clickstream_event_functions_resolve_category_view_no_previous_category_still_returns_valid_category():
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
