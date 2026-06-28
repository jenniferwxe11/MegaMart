import copy
import random
from datetime import timedelta

import pandas as pd
import pytest

from data_generation.config.clickstreams_config import (
    MISSION_SCROLL_BIAS,
    PROMOTION_TYPE_MULTIPLIER,
    VALID_EVENT_TRANSITIONS,
)
from data_generation.config.constants import SEASONAL_DATES
from data_generation.config.store_products_config import ESSENTIAL_CATEGORIES
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
    _build_datetime,
)

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


def test_clickstream_transition_functions_apply_seasonal_uplift_season_increases_target_transitions():
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


def test_clickstream_transition_functions_apply_seasonal_uplift_evening_increases_target_transitions():
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


def test_clickstream_transition_functions_apply_seasonal_uplift_payday_increases_target_transitions():
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


def test_clickstream_transition_functions_apply_seasonal_uplift_weekend_increases_target_transitions():
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


def test_clickstream_transition_functions_promotion_engagement_probability_relevant_scope_higher_than_irrelevant():
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


def test_clickstream_transition_functions_promotion_engagement_probability_bundle_cap_at_10():
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


def test_clickstream_transition_functions_promotion_engagement_probability_dollar_discount_cap_at_5():
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


def test_clickstream_transition_functions_promotion_engagement_probability_unknown_mechanic_handling():
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


def test_clickstream_transition_functions_promotion_perception_accuracy():
    dollar = promotion_perception_accuracy({"promotion_mechanic": "dollar_discount"})
    percentage = promotion_perception_accuracy(
        {"promotion_mechanic": "percentage_discount"}
    )
    bundle = promotion_perception_accuracy({"promotion_mechanic": "bundle"})
    assert percentage > dollar > bundle


# ============================================================
# apply_promotion_uplift()
# ============================================================


def test_clickstream_transition_functions_apply_promotion_uplift_config_validity():
    for _, config in PROMOTION_TYPE_MULTIPLIER.items():
        assert config["atc_multiplier"][0] <= config["atc_multiplier"][1]
        assert config["checkout_multiplier"][0] <= config["checkout_multiplier"][1]
        assert config["remove_multiplier"][0] <= config["remove_multiplier"][1]


def test_clickstream_transition_functions_apply_promotion_uplift_free_shipping_effect():
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


def test_clickstream_transition_functions_apply_promotion_uplift_discount_types_stronger_than_free_shipping():
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


def test_clickstream_transition_functions_apply_promotion_uplift_bundle_reduces_cart_removal():
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


def test_clickstream_transition_functions_apply_promotion_uplift_multiple_promotions_increase_uplift():
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
# is never read. ctx is passed only because the
# function signature requires ctx — the patched function ignores it.


def test_clickstream_transition_functions_apply_stock_status_uplift_out_of_stock(
    ctx, monkeypatch
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
        ctx,
        transition_probability,
        store_id="STOR001",
        product_id="PROD001",
        timestamp=_build_datetime(),
    )

    assert "Add to Cart" not in result["Product View"]
    assert result["Product View"]["Home View"] == 1.2
    assert result["Product View"]["Category View"] == 1.3
    assert result["Product View"]["Search View"] == 1.2


def test_clickstream_transition_functions_apply_stock_status_uplift_low_stock(
    ctx, monkeypatch
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
        ctx,
        transition_probability,
        store_id="STOR001",
        product_id="PROD001",
        timestamp=_build_datetime(),
    )

    assert result["Product View"]["Add to Cart"] == 1.2
    assert result["Product View"]["Home View"] == 1.0


def test_clickstream_transition_functions_apply_stock_status_uplift_in_stock(
    ctx, monkeypatch
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
        ctx,
        transition_probability,
        store_id="STOR001",
        product_id="PROD001",
        timestamp=_build_datetime(),
    )

    assert result["Product View"]["Add to Cart"] == 1.1


def test_clickstream_transition_functions_apply_stock_status_uplift_no_product_id(ctx):
    base = {
        "Product View": {
            "Add to Cart": 1.0,
        }
    }

    result = apply_stock_status_uplift(
        ctx,
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
def test_clickstream_transition_functions_get_base_transition_probability(
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


def test_clickstream_transition_functions_apply_mission_bias_no_previous_event_type(
    seed: int = 42,
):
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


def test_clickstream_transition_functions_apply_mission_bias_unknown_mission():
    transition_probability = _base_transition_probability()
    result = apply_mission_bias(
        event_transition_probability=transition_probability,
        mission_choice="UNKNOWN_MISSION",
        previous_event_type="Product View",
        progress=0.5,
    )

    assert result == transition_probability


def test_clickstream_transition_functions_apply_mission_bias_previous_event_not_found(
    seed: int = 42,
):
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


def test_clickstream_transition_functions_apply_mission_bias_applies_multiplier(
    seed: int = 42,
):
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


def test_clickstream_transition_functions_apply_mission_bias_checkout_progress_scaling(
    seed: int = 42,
):
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


def test_clickstream_transition_functions_apply_purchase_progress_bias_missing_previous_event():
    base = _base_transition_probability()
    result = apply_purchase_progress_bias(
        base,
        previous_event_type=None,
        previous_category=None,
        events=[],
        progress=0.3,
    )

    assert result == base


def test_clickstream_transition_functions_apply_purchase_progress_bias_early_stage_add_to_cart_streak_encourage_browsing():
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


def test_clickstream_transition_functions_apply_purchase_progress_bias_early_stage_add_to_cart_streak_discourage_checkout():
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


def test_clickstream_transition_functions_apply_purchase_progress_bias_mid_stage():
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


def test_clickstream_transition_functions_apply_purchase_progress_bias_late_stage_discourage_browsing_encourage_checkout():
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


def test_clickstream_transition_functions_apply_purchase_progress_bias_essential_category_boost_atc(
    seed: int = 42,
):
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


def test_clickstream_transition_functions_normalise_probability_basic_normalisation():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)
    pv = result["Product View"]

    assert pv["Add to Cart"] == 2.0 / (2.0 + 1.5 + 0.85)
    assert pv["Search View"] == 1.5 / (2.0 + 1.5 + 0.85)
    assert pv["Cart View"] == 0.85 / (2.0 + 1.5 + 0.85)
    assert abs(sum(pv.values()) - 1.0) < 1e-9


def test_clickstream_transition_functions_normalise_probability_preserves_ratios():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)
    pv = result["Product View"]

    ratio_original = 2.0 / 0.85
    ratio_normalized = pv["Add to Cart"] / pv["Cart View"]

    assert abs(ratio_original - ratio_normalized) < 1e-9


def test_clickstream_transition_functions_normalise_probability_zero_total_unchanged():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)
    pv = result["Checkout Start"]

    assert pv["Payment Attempt"] == 0.0


def test_clickstream_transition_functions_normalise_probability_independent_event_groups():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)

    pv_sum = sum(result["Product View"].values())
    cv_sum = sum(result["Cart View"].values())

    assert abs(pv_sum - 1.0) < 1e-9
    assert abs(cv_sum - 1.0) < 1e-9


def test_clickstream_transition_functions_normalise_probability_single_transition():
    base = _unnormalised_base_transition_probability()
    result = normalise_probability(base)

    assert result["Search View"]["Product View"] == 1.0
