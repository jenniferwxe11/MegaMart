import random

import pandas as pd
import pytest

from data_generation.config.promotions_config import (
    BUNDLE_CAMPAIGN_COMPATIBILITY,
    CAMPAIGN_PROMOTION_STRATEGY,
)
from data_generation.services.bundles.bundle_lifecycle_service import bundle_lifecycle
from data_generation.services.promotions.promotion_service import (
    select_active_product_in_timeframe,
    select_bundle_for_campaign,
)
from tests.helpers import (
    _build_bundle_products_dict,
    _build_category,
    _build_datetime_range,
)

pytestmark = pytest.mark.skip(reason="Temporarily disabled")
# ============================================================
# bundle_lifecycle()
# ============================================================
# Integration contract: uses product lifecycle data


def test_bundle_promotion_flow_bundle_lifecycle_properties(ctx):
    selected_products = _build_bundle_products_dict(ctx)
    start, end = bundle_lifecycle(ctx, selected_products)
    launch_map = ctx.product_lifecycles.product_launch_map
    discontinuation_map = ctx.product_lifecycles.product_discontinuation_map

    launches = [
        launch_map[pid]
        for pid, _ in selected_products
        if pid in launch_map and not pd.isna(launch_map[pid])
    ]

    discontinuations = [
        discontinuation_map[pid]
        for pid, _ in selected_products
        if pid in discontinuation_map and not pd.isna(discontinuation_map[pid])
    ]

    if launches:
        assert start >= max(launches)

    if discontinuations:
        assert end <= min(discontinuations)

    assert start <= end
    assert (end - start).days <= 120


# ============================================================
# select_bundle_for_campaign()
# ============================================================
# Integration contract: uses product lifecycle + bundle data


def test_bundle_promotion_flow_select_bundle_for_campaign(ctx, seed: int = 42):
    rng = random.Random(seed)
    start, end = _build_datetime_range()
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))

    bundle = select_bundle_for_campaign(
        ctx,
        campaign_type,
        start,
        end,
    )

    if bundle is None:
        return

    df = ctx.bundles.bundle_full_df

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
# select_active_product_in_timeframe()
# ============================================================
# Integration contract: uses product lifecycle data


def test_bundle_promotion_flow_select_active_product_in_timeframe(
    ctx,
):
    category = _build_category(ctx, 1)[0]
    start, end = _build_datetime_range()

    pid = select_active_product_in_timeframe(
        ctx,
        category,
        start,
        end,
    )

    if pid is not None:
        df = ctx.product_lifecycles.product_with_lifecycle_df
        row = df[df["product_id"] == pid].iloc[0]

        assert row["category"] == category
        assert pd.notna(row["launch_date"]) and row["launch_date"] <= start
        assert (
            pd.isna(row["discontinuation_date"]) or row["discontinuation_date"] >= end
        )
