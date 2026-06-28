import random

import pytest

from data_generation.services.clickstreams.clickstream_promotion_service import (
    process_promotion_exposure,
)

# ============================================================
# process_promotion_exposure()
# ============================================================
# Integration contract: uses bundle + promotion data


def test_promotion_exposure_flow_process_promotion_exposure_returns_none_for_empty_promotions(
    ctx,
):
    """
    Integration contract: no relevant promotions → (None, None).
    """
    seen_promotions: dict = {}
    seen_promo_types: dict = {}
    selected_promotions: list = []
    pending_events: list = []

    promo_ids, bundle_ids = process_promotion_exposure(
        ctx,
        relevant_promotions=[],
        event_type="Product View",
        product_id=None,
        seen_promotions=seen_promotions,
        seen_promo_types=seen_promo_types,
        selected_promotions=selected_promotions,
        pending_events=pending_events,
    )

    assert promo_ids is None
    assert bundle_ids is None


def test_promotion_exposure_flow_process_promotion_exposure_product_promo_injects_add_to_cart_pending_event(
    monkeypatch, ctx
):
    """
    Integration contract: a product-scope promotion seen on its own product
    page must inject an "Add to Cart" pending event for that product.
    Tests that process_promotion_exposure() correctly reads bundle_dict
    and injects pending events based on real promotion + bundle data.
    """
    df = ctx.promotions.promotions_df
    product_promos = df[df["promotion_scope"] == "product"]
    if product_promos.empty:
        pytest.skip("No product-scope promotions in generated data")

    promo_row = product_promos.iloc[0]
    product_id = promo_row["promotion_target_id"]

    relevant_promotions = [
        {
            "promotion_id": promo_row["promotion_id"],
            "promotion_scope": "product",
            "promotion_target_id": product_id,
            "promotion_mechanic": promo_row["promotion_mechanic"],
            "bundle_id": None,
        }
    ]

    seen_promotions: dict = {}
    seen_promo_types: dict = {}
    selected_promotions: list = []
    pending_events: list = []

    # Force engagement + perception to both succeed
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_promotion_service.promotion_engagement_probability",
        lambda *args, **kwargs: 1.0,
    )
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_promotion_service.promotion_perception_accuracy",
        lambda *args, **kwargs: 1.0,
    )

    monkeypatch.setattr(random, "random", lambda: 0.0)  # always < any probability

    process_promotion_exposure(
        ctx,
        relevant_promotions=relevant_promotions,
        event_type="Product View",
        product_id=product_id,
        seen_promotions=seen_promotions,
        seen_promo_types=seen_promo_types,
        selected_promotions=selected_promotions,
        pending_events=pending_events,
    )

    add_to_cart_events = [
        e
        for e in pending_events
        if e.get("type") == "Add to Cart" and e.get("product_id") == product_id
    ]
    assert (
        len(add_to_cart_events) >= 1
    ), f"Expected Add to Cart pending event for product {product_id}"


def test_promotion_exposure_flow_process_promotion_exposure_seen_promotions_counter_increments(
    ctx,
):
    """
    Integration contract: each exposure increments the seen counter,
    which drives the fatigue curve in the transition probability model.
    """
    df = ctx.promotions.promotions_df
    promo_row = df.iloc[0]

    relevant_promotions = [
        {
            "promotion_id": promo_row["promotion_id"],
            "promotion_scope": promo_row["promotion_scope"],
            "promotion_target_id": promo_row["promotion_target_id"],
            "promotion_mechanic": promo_row["promotion_mechanic"],
            "bundle_id": None,
        }
    ]

    seen_promotions: dict = {}
    seen_promo_types: dict = {}

    # Call twice to simulate two exposures
    for _ in range(2):
        process_promotion_exposure(
            ctx,
            relevant_promotions=relevant_promotions,
            event_type="Cart View",
            product_id=None,
            seen_promotions=seen_promotions,
            seen_promo_types=seen_promo_types,
            selected_promotions=[],
            pending_events=[],
        )

    assert (
        seen_promotions.get(promo_row["promotion_id"], 0) == 2
    ), "seen_promotions counter should be 2 after two exposures"


def test_promotion_exposure_flow_process_promotion_exposure_bundle_promo_injects_full_bundle_pending_events(
    monkeypatch, ctx
):
    """
    Integration contract: a bundle promotion seen on a bundle product's page
    must inject Product View + Add to Cart events for all bundle members.
    Tests that process_promotion_exposure() reads the real bundle_dict.
    """
    df = ctx.promotions.promotions_df
    bundle_promos = df[df["promotion_scope"] == "bundle"]
    if bundle_promos.empty:
        pytest.skip("No bundle-scope promotions in generated data")

    promo_row = bundle_promos.iloc[0]
    bundle_id = promo_row["promotion_target_id"]
    bundle_dict = ctx.bundles.bundle_dict
    bundle_products = bundle_dict.get(bundle_id, {})
    anchor_product_id = list(bundle_products.keys())[0]

    relevant_promotions = [
        {
            "promotion_id": promo_row["promotion_id"],
            "promotion_scope": "bundle",
            "promotion_target_id": bundle_id,
            "promotion_mechanic": "bundle",
            "bundle_id": bundle_id,
        }
    ]

    seen_promotions: dict = {}
    seen_promo_types: dict = {}
    selected_promotions: list = []
    pending_events: list = []

    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_promotion_service.promotion_engagement_probability",
        lambda *args, **kwargs: 1.0,
    )
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_promotion_service.promotion_perception_accuracy",
        lambda *args, **kwargs: 1.0,
    )
    monkeypatch.setattr(random, "random", lambda: 0.0)

    process_promotion_exposure(
        ctx,
        relevant_promotions=relevant_promotions,
        event_type="Product View",
        product_id=anchor_product_id,
        seen_promotions=seen_promotions,
        seen_promo_types=seen_promo_types,
        selected_promotions=selected_promotions,
        pending_events=pending_events,
    )

    # pending_types = [e["type"] for e in pending_events]
    pending_products = [e.get("product_id") for e in pending_events]

    # All bundle products should be covered
    for pid in bundle_products:
        assert (
            pid in pending_products
        ), f"Bundle product {pid} missing from pending events"

    # Non-anchor products should have a Product View event injected before Add to Cart
    non_anchor = [p for p in bundle_products if p != anchor_product_id]
    for pid in non_anchor:
        pid_events = [e["type"] for e in pending_events if e.get("product_id") == pid]
        assert (
            "Product View" in pid_events
        ), f"Missing Product View for non-anchor bundle product {pid}"
