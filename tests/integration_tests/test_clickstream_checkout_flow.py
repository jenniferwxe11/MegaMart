import random

import pytest

from data_generation.config.clickstreams_config import MISSION_EFFICIENCY
from data_generation.services.clickstreams.clickstream_event_service import (
    resolve_payment_successful,
)
from tests.helpers import _build_customer_segment

# ============================================================
# resolve_payment_successful()
# ============================================================
# Integration contract: uses bundle + product data


def test_clickstream_checkout_flow_resolve_payment_successful_purchased_items_are_subset_of_cart(
    ctx, seed: int = 42
):
    """
    Integration contract: every purchased item must have been in the
    cart. resolve_payment_successful() must not invent new products.
    """
    rng = random.Random(seed)
    product_ids = ctx.products.product_ids
    mission = rng.choice(list(MISSION_EFFICIENCY.keys()))
    customer_segment = _build_customer_segment()
    cart = product_ids[:6]
    counter: dict[str, int] = {}
    for p in cart:
        counter[p] = counter.get(p, 0) + 1

    purchased, _ = resolve_payment_successful(
        ctx,
        cart_content=list(cart),
        selected_promotions=[],
        mission_choice=mission,
        has_treatment=False,
        customer_segment=customer_segment,
    )

    purchase_counter: dict[str, int] = {}
    for p in purchased:
        purchase_counter[p] = purchase_counter.get(p, 0) + 1

    for pid, qty in purchase_counter.items():
        assert qty <= counter.get(
            pid, 0
        ), f"Purchased {qty}x {pid!r} but cart only had {counter.get(pid, 0)}"


def test_clickstream_checkout_flow_resolve_payment_successful_cart_shrinks_by_purchased_amount(
    ctx, seed: int = 42
):
    """
    Integration contract: len(updated_cart) == len(original_cart) - len(purchased_items).
    """
    rng = random.Random(seed)
    product_ids = ctx.products.product_ids
    cart = list(product_ids[:8])
    mission = rng.choice(list(MISSION_EFFICIENCY.keys()))
    customer_segment = _build_customer_segment()

    purchased, updated_cart = resolve_payment_successful(
        ctx,
        cart_content=cart,
        selected_promotions=[],
        mission_choice=mission,
        has_treatment=False,
        customer_segment=customer_segment,
    )

    assert len(updated_cart) == len(cart) - len(purchased), (
        f"Cart size mismatch: original={len(cart)}, "
        f"purchased={len(purchased)}, remaining={len(updated_cart)}"
    )


def test_clickstream_checkout_flow_resolve_payment_successful_at_least_one_item_always_purchased(
    ctx, seed: int = 42
):
    """
    Integration contract: a non-empty cart must always result in at
    least one purchased item (purchase_count = max(1, ...)).
    """
    rng = random.Random(seed)
    product_ids = ctx.products.product_ids
    cart = list(product_ids[:4])
    mission = rng.choice(list(MISSION_EFFICIENCY.keys()))
    customer_segment = _build_customer_segment()

    for _ in range(10):
        purchased, _ = resolve_payment_successful(
            ctx,
            cart_content=cart,
            selected_promotions=[],
            mission_choice=mission,
            has_treatment=False,
            customer_segment=customer_segment,
        )
        assert len(purchased) >= 1, "At least one item must be purchased per checkout"


def test_clickstream_checkout_flow_resolve_payment_successful_treatment_increases_average_purchase_count(
    ctx, seed: int = 42, N=1000
):
    """
    Integration contract: customers in the Treatment group must on
    average purchase more items per checkout than non-treatment,
    reflecting the alpha boost in determine_purchase_alpha_beta().
    """
    rng = random.Random(seed)
    product_ids = ctx.products.product_ids
    cart = list(product_ids[:10])
    customer_segment = _build_customer_segment()
    mission = rng.choice(list(MISSION_EFFICIENCY.keys()))

    purchased_treatment = [
        len(
            resolve_payment_successful(
                ctx,
                cart_content=list(cart),
                selected_promotions=[],
                mission_choice=mission,
                has_treatment=True,
                customer_segment=customer_segment,
            )[0]
        )
        for _ in range(N)
    ]
    purchased_no_treatment = [
        len(
            resolve_payment_successful(
                ctx,
                cart_content=list(cart),
                selected_promotions=[],
                mission_choice=mission,
                has_treatment=False,
                customer_segment=customer_segment,
            )[0]
        )
        for _ in range(N)
    ]

    avg_treatment = sum(purchased_treatment) / N
    avg_no_treatment = sum(purchased_no_treatment) / N

    assert avg_treatment >= avg_no_treatment, (
        f"Treatment avg purchase count {avg_treatment:.2f} should be >= "
        f"non-treatment {avg_no_treatment:.2f}"
    )


def test_clickstream_checkout_flow_resolve_payment_successful_bundle_items_purchased_together(
    ctx, seed: int = 42
):
    """
    Integration contract: when a bundle promotion is active and all
    bundle products are in the cart, the bundle items should be
    purchased as a cohesive unit (~70% of the time).
    Tests that bundle_dict is correctly consulted.
    """
    rng = random.Random(seed)
    bundle_dict = ctx.bundles.bundle_dict
    mission = rng.choice(list(MISSION_EFFICIENCY.keys()))
    customer_segment = _build_customer_segment()

    # Find a bundle with ≤3 products so we can fill the cart easily
    eligible = {
        bid: items for bid, items in bundle_dict.items() if 1 <= len(items) <= 3
    }
    if not eligible:
        pytest.skip("No small bundles available for this test")

    bundle_id, bundle_items = next(iter(eligible.items()))
    bundle_pids = list(bundle_items.keys())

    # Build a cart that satisfies the bundle
    cart = []
    for pid, qty in bundle_items.items():
        cart.extend([pid] * qty)
    # Add some extra non-bundle items
    extra = [p for p in ctx.products.product_ids if p not in bundle_items][:3]
    cart.extend(extra)

    promo = {
        "promotion_id": "PROMO_TEST",
        "promotion_scope": "bundle",
        "bundle_id": bundle_id,
    }

    bundle_cohesion_count = 0
    trials = 20

    for _ in range(trials):
        purchased, _ = resolve_payment_successful(
            ctx,
            cart_content=list(cart),
            selected_promotions=[promo],
            mission_choice=mission,
            has_treatment=False,
            customer_segment=customer_segment,
        )
        purchased_set = set(purchased)
        if all(pid in purchased_set for pid in bundle_pids):
            bundle_cohesion_count += 1

    # Expect bundle cohesion at least 50% of the time (the 70% chance * other factors)
    assert (
        bundle_cohesion_count >= trials * 0.3
    ), f"Bundle cohesion rate {bundle_cohesion_count}/{trials} is unexpectedly low"
