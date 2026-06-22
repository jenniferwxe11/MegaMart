import random

import pandas as pd

from data_generation.config.campaigns_config import (
    CAMPAIGN_PEAK_CATEGORIES,
    CATEGORY_CODE_MAP,
)
from data_generation.config.constants import DATA_END_DATE
from data_generation.config.promotions_config import (
    BUNDLE_CAMPAIGN_COMPATIBILITY,
    CAMPAIGN_PROMOTION_STRATEGY,
    CATEGORY_PROMOTION_PROB,
    CHANNEL_PROMOTION_COMPATIBILITY,
)
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
from tests.unit_tests.helpers import (
    _build_bundle,
    _build_category,
    _build_customer_segment,
    _build_date_range,
    _build_datetime_range,
    _build_promotion_value,
    _build_promotion_variables,
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

    if campaign_type == "Seasonal":
        campaign_categories = CAMPAIGN_PEAK_CATEGORIES[campaign_type]
        season: str | None = None

        if isinstance(campaign_categories, dict):
            season = rng.choice(list(campaign_categories.keys()))
            seasonal_pool = campaign_categories.get(season, [])
        else:
            season = None

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


def test_promotion_select_product_in_category_valid(product_ctx):
    category = _build_category(product_ctx, 1)[0]
    result = select_product_in_category(product_ctx, category)
    valid_products = product_ctx.products.category_to_products[category]
    assert result is None or result in valid_products


# ============================================================
# select_active_product_in_timeframe()
# ============================================================


def test_promotion_select_active_product_in_timeframe(product_lifecycle_ctx):
    category = _build_category(product_lifecycle_ctx, 1)[0]
    start, end = _build_datetime_range()

    pid = select_active_product_in_timeframe(
        product_lifecycle_ctx,
        category,
        start,
        end,
    )

    if pid is not None:
        df = product_lifecycle_ctx.product_lifecycles.product_with_lifecycle_df
        row = df[df["product_id"] == pid].iloc[0]

        assert row["category"] == category
        assert pd.notna(row["launch_date"]) and row["launch_date"] <= start
        assert (
            pd.isna(row["discontinuation_date"]) or row["discontinuation_date"] >= end
        )


# ============================================================
# select_bundle_for_campaign()
# ============================================================


def test_promotion_select_bundle_for_campaign(bundle_ctx, seed: int = 42):
    rng = random.Random(seed)
    start, end = _build_datetime_range()
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))

    bundle = select_bundle_for_campaign(
        bundle_ctx,
        campaign_type,
        start,
        end,
    )

    if bundle is None:
        return

    df = bundle_ctx.bundles.bundle_full_df

    # Bundle exists in dataset
    matched = df[df["bundle_pricing_id"] == bundle["bundle_pricing_id"]]
    assert not matched.empty, "Returned bundle_pricing_id not found in source data"

    row = matched.iloc[0]

    # Return variable structure validation
    assert "bundle_pricing_id" in bundle
    assert "bundle_price" in bundle
    assert "discount_value" in bundle
    assert "categories" in bundle

    # Bundle type campaign compatibility
    allowed_types = BUNDLE_CAMPAIGN_COMPATIBILITY.get(campaign_type, [])
    assert row["bundle_type"] in allowed_types

    # Timeframe correctness
    assert row["effective_start_date"] <= start
    assert row["effective_end_date"] >= end

    # Data integrity (returned == source)
    assert bundle["bundle_pricing_id"] == row["bundle_pricing_id"]
    assert bundle["bundle_price"] == row["bundle_price"]
    assert bundle["discount_value"] == row["discount_value"]
    assert bundle["categories"] == row["categories"]


# ============================================================
# generate_promotion_value()
# ============================================================


def test_promotion_generate_promotion_value(bundle_ctx, seed: int = 42):
    rng = random.Random(seed)
    category = _build_category(bundle_ctx, 1)[0]
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    bundle = _build_bundle(bundle_ctx)
    promotion_mechanic, promotion_scope, promotion_target_id, category = (
        _build_promotion_variables(bundle_ctx)
    )

    value = generate_promotion_value(
        bundle_ctx,
        promotion_mechanic,
        promotion_scope,
        promotion_target_id,
        category,
        campaign_type,
        bundle,
    )

    if promotion_mechanic == "percentage_discount":
        assert 0 <= value <= 40
    elif promotion_mechanic == "free_shipping":
        assert value == 0.0
    else:
        assert value >= 0 and isinstance(value, (int, float))


# ============================================================
# generate_promotion_name()
# ============================================================


def test_promotion_generate_promotion_name_returns_string(bundle_ctx, seed: int = 42):
    rng = random.Random(seed)
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    promotion_mechanic, promotion_scope, _, category = _build_promotion_variables(
        bundle_ctx
    )
    campaign_categories = CAMPAIGN_PEAK_CATEGORIES[campaign_type]
    season: str | None = None

    if isinstance(campaign_categories, dict):
        season = rng.choice(list(campaign_categories.keys()))
    else:
        season = None

    name = generate_promotion_name(
        promotion_mechanic,
        promotion_scope,
        category,
        season,
    )

    assert isinstance(name, str)
    assert len(name) > 0


# ============================================================
# get_min_spend()
# ============================================================


def test_promotion_get_min_spend(bundle_ctx, seed: int = 42):
    rng = random.Random(seed)
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    promotion_mechanic, promotion_scope, promotion_target_id, category = (
        _build_promotion_variables(bundle_ctx)
    )
    promotion_value = _build_promotion_value(
        bundle_ctx, promotion_mechanic, promotion_scope, promotion_target_id, category
    )
    val = get_min_spend(
        promotion_mechanic,
        promotion_scope,
        promotion_value,
        category,
        campaign_type,
    )

    assert val is None or val >= 0


# ============================================================
# generate_discount_code()
# ============================================================


def test_promotion_generate_discount_code_structure(
    campaign_ctx, bundle_ctx, seed: int = 42
):
    rng = random.Random(seed)
    promotion_mechanic, promotion_scope, promotion_target_id, category = (
        _build_promotion_variables(bundle_ctx)
    )
    promotion_value = _build_promotion_value(
        bundle_ctx, promotion_mechanic, promotion_scope, promotion_target_id, category
    )
    df = campaign_ctx.campaigns.campaigns_df
    campaign_id = df.iloc[rng.randrange(len(df))]["campaign_id"]
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
