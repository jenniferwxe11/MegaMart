import random

import pandas as pd

from data_generation.config.campaigns_config import (
    CAMPAIGN_PEAK_CATEGORIES,
    CATEGORY_CODE_MAP,
)
from data_generation.config.constants import DATA_END_DATE
from data_generation.config.promotions_config import (
    CAMPAIGN_PROMOTION_STRATEGY,
    CATEGORY_PROMOTION_PROB,
    CHANNEL_PROMOTION_COMPATIBILITY,
    PROMOTION_TYPE_PROB,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    check_promotion_eligibility,
)
from data_generation.services.promotions.promotion_service import (
    generate_discount_code,
    generate_promotion_name,
    generate_promotion_value,
    get_min_spend,
    safe_date_window,
    select_category,
    select_product_in_category,
    select_promotion_mechanics,
)
from tests.helpers import (
    _build_bundle,
    _build_campaign,
    _build_category,
    _build_customer_segment,
    _build_date_range,
    _build_datetime,
)

# ============================================================
# safe_date_window()
# ============================================================


def test_promotion_safe_date_window_never_inverts():
    start, end = _build_date_range()
    s, e = safe_date_window(start, end, pd.Timestamp(DATA_END_DATE))
    assert s <= e


# ============================================================
# select_promotion_mechanics()
# ============================================================


def test_promotion_select_promotion_mechanics_properties(seed: int = 42):
    rng = random.Random(seed)
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    channels = rng.sample(
        list(CHANNEL_PROMOTION_COMPATIBILITY.keys()), k=rng.randint(1, 2)
    )
    result = select_promotion_mechanics(campaign_type, channels)
    strategy = CAMPAIGN_PROMOTION_STRATEGY[campaign_type]
    allowed = {
        promo
        for ch in channels
        for promo in CHANNEL_PROMOTION_COMPATIBILITY.get(ch, [])
    }
    valid_promotions = set(strategy["primary"]) | set(strategy["secondary"])
    min_promo, max_promo = strategy.get("promo_count", (1, 2))

    # List structure
    assert isinstance(result, list)

    # Respects configured number of promotions
    assert isinstance(min_promo, int)
    assert isinstance(max_promo, int)
    assert min_promo <= len(result) <= max_promo

    # Only returns strategy defined promotion mechanics
    assert all(p in valid_promotions for p in result)

    # Respects channel promotion constraints
    assert all(p in allowed for p in result)

    # Primary promotion mechanics are prioritised when available
    primary = [p for p in strategy["primary"] if p in allowed]
    if primary:
        assert result[0] in primary

    # No duplicate promotion mechanics
    assert len(result) == len(set(result))


# ============================================================
# select_category()
# ============================================================


def test_promotion_select_category_returns_valid(seed: int = 42):
    rng = random.Random(seed)
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    target_segment = _build_customer_segment()
    seasonal_pool: list[str] = []
    season: str | None = None

    if campaign_type == "Seasonal":
        campaign_categories = CAMPAIGN_PEAK_CATEGORIES[campaign_type]

        if isinstance(campaign_categories, dict):
            season = rng.choice(list(campaign_categories.keys()))
            seasonal_pool = campaign_categories.get(season, [])

    fallback_pool = list(CATEGORY_PROMOTION_PROB.keys())

    result = select_category(campaign_type, season, target_segment)
    base_pool = seasonal_pool if seasonal_pool else fallback_pool
    valid_set = set(base_pool)

    assert isinstance(result, str)
    assert len(result) > 0
    assert result in valid_set


# ============================================================
# select_product_in_category()
# ============================================================
# UNIT: reads only products_df (single table, no lifecycle join).
# product_ctx is the lightest ctx fixture.


def test_promotion_select_product_in_category_valid(product_ctx):
    category = _build_category(product_ctx, 1)[0]
    result = select_product_in_category(product_ctx, category)
    valid_products = product_ctx.products.category_to_products[category]
    assert result is None or result in valid_products


# ============================================================
# generate_promotion_value()
# ============================================================
# UNIT: reads products_df for price lookups. Logic under test is
# the discount calculation, not lifecycle or bundle validity.


def test_promotion_generate_promotion_value_percentage_discount(
    bundle_ctx, seed: int = 42
):
    rng = random.Random(seed)
    bundle = _build_bundle(bundle_ctx)

    value = generate_promotion_value(
        bundle_ctx,
        promotion_mechanic="percentage_discount",
        promotion_scope="category",
        promotion_target_id="Beverages",
        category="Beverages",
        campaign_type=rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys())),
        bundle=bundle,
    )

    assert 0 <= value <= 40
    assert isinstance(value, (int, float))


def test_promotion_generate_promotion_value_free_shipping(bundle_ctx):
    bundle = _build_bundle(bundle_ctx)

    value = generate_promotion_value(
        bundle_ctx,
        promotion_mechanic="free_shipping",
        promotion_scope="cart",
        promotion_target_id=None,
        category=None,
        campaign_type="Retention",
        bundle=bundle,
    )

    assert value == 0.0
    assert isinstance(value, (int, float))


# ============================================================
# generate_promotion_name()
# ============================================================


def test_promotion_generate_promotion_name_returns_string():
    name = generate_promotion_name(
        promotion_mechanic="dollar_discount",
        promotion_scope="product",
        category="PROD001",
        season="Black Friday",
    )

    assert isinstance(name, str)
    assert len(name) > 0


# ============================================================
# get_min_spend()
# ============================================================


def test_promotion_get_min_spend():
    val = get_min_spend(
        promotion_mechanic="percentage_discount",
        promotion_scope="product",
        promotion_value=10,
        category="Beverages",
        campaign_type="Seasonal",
    )

    assert val is None or val >= 0


# ============================================================
# generate_discount_code()
# ============================================================
# UNIT: pure string assembly. Uses campaign_ctx only to get a
# real campaign_id string — no DataFrame traversal.


def test_promotion_generate_discount_code_structure(campaign_ctx, seed: int = 42):
    rng = random.Random(seed)
    promotion_mechanic = rng.choice(list(PROMOTION_TYPE_PROB.keys()))
    promotion_scope = rng.choice(["cart", "category", "product"])
    promotion_target_id = "Beverages"
    promotion_value = rng.randint(5, 10)
    campaign_id = _build_campaign(campaign_ctx)["campaign_id"]
    code = generate_discount_code(
        promotion_mechanic,
        promotion_scope,
        promotion_target_id,
        promotion_value,
        campaign_id,
    )

    assert isinstance(code, str)

    parts = code.split("_")

    # Campaign id always first if provided
    assert parts[0] == campaign_id

    # Target encoding correctness
    if promotion_scope == "category":
        expected_target = CATEGORY_CODE_MAP.get(promotion_target_id)
    else:
        expected_target = promotion_target_id

    if expected_target:
        assert expected_target in parts

    # Value rules
    if promotion_mechanic != "free_shipping" and promotion_value:
        assert str(int(promotion_value)) in parts
    else:
        assert (
            all(not p.isdigit() for p in parts[2:])
            or promotion_mechanic == "free_shipping"
        )


# ============================================================
# check_promotion_eligibility()
# ============================================================
# UNIT: the filtering logic is what's under test. We mock
# get_active_promotions so no real promotions_df is read.
# promotion_ctx is passed only because the function signature
# requires ctx — the mock intercepts before ctx is used.


def test_check_promotion_eligibility_treatment_sees_global_and_treatment_promotions(
    monkeypatch, promotion_ctx
):
    """
    Treatment customer should see both promos linked to their treatment campaign
    and from global (campaign_id=None)
    """
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_lookup_service.get_active_promotions",
        lambda *args, **kwargs: [
            {"promotion_id": "PROMO001", "campaign_id": None},
            {"promotion_id": "PROMO002", "campaign_id": "CAMP001"},
            {"promotion_id": "PROMO003", "campaign_id": "CAMP002"},
        ],
    )

    timestamp = _build_datetime()
    active_campaigns = pd.DataFrame(
        [
            {"campaign_id": "CAMP001", "assignment_group": "Treatment"},
            {"campaign_id": "CAMP002", "assignment_group": "Control"},
        ]
    )

    result = check_promotion_eligibility(promotion_ctx, timestamp, active_campaigns)

    # Treatment sees: PROMO001 (global) + PROMO002 (CAMP001 = treatment)
    # NOT PROMO003 (CAMP002 = control only)
    assert len(result) == 2
    ids = {p["promotion_id"] for p in result}
    assert "PROMO001" in ids
    assert "PROMO002" in ids
    assert "PROMO003" not in ids


def test_check_promotion_eligibility_control_sees_global_promotions(
    monkeypatch, promotion_ctx
):
    """
    Control only customer should see only global promotions.
    """
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_lookup_service.get_active_promotions",
        lambda *args, **kwargs: [
            {"promotion_id": "PROMO001", "campaign_id": None},
            {"promotion_id": "PROMO002", "campaign_id": "CAMP001"},
        ],
    )

    timestamp = _build_datetime()
    active_campaigns = pd.DataFrame(
        [
            {"campaign_id": "CAMP001", "assignment_group": "Control"},
        ]
    )

    result = check_promotion_eligibility(promotion_ctx, timestamp, active_campaigns)

    assert len(result) == 1
    assert result[0]["promotion_id"] == "PROMO001"


def test_check_promotion_eligibility_no_campaigns_sees_global_promotions(
    monkeypatch, promotion_ctx
):
    """
    No active campaigns → only global promotions (campaign_id=None) returned.
    """
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_lookup_service.get_active_promotions",
        lambda *args, **kwargs: [
            {"promotion_id": "PROMO001", "campaign_id": None},
            {"promotion_id": "PROMO002", "campaign_id": "CAMP001"},
        ],
    )

    timestamp = _build_datetime()
    result = check_promotion_eligibility(promotion_ctx, timestamp, None)

    assert len(result) == 1
    assert result[0]["promotion_id"] == "PROMO001"
