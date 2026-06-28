import random
from typing import cast

import pandas as pd
import pytest
from faker import Faker

from data_generation.services.transactions.transaction_lookup_service import (
    get_active_bundle_pricing,
)
from data_generation.services.transactions.transaction_promotion_service import (
    apply_cart_level_discount,
    get_eligible_promotions,
    resolve_promotion_stack,
)
from tests.helpers import (
    _build_bundle_promotion,
    _build_cart_items_for_promotion,
    _build_customer_segment,
    _build_datetime,
    _build_non_shipping_promotion,
    _build_promotion,
    _build_two_compatible_promotions,
)

fake = Faker()
fake.seed_instance(42)


# ============================================================
# get_eligible_promotions()
# ============================================================
# Integration contract: uses promotion + transaction data


def test_transaction_promotion_flow_get_eligible_promotions_returns_list(
    ctx, seed: int = 42
):
    rng = random.Random(seed)
    promo = _build_promotion(ctx, rng)
    transaction_time = fake.date_time_between(
        start_date=promo["effective_start_date"], end_date=promo["effective_end_date"]
    )
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    cart_subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
    result = get_eligible_promotions(ctx, transaction_time, cart_items, cart_subtotal)

    assert isinstance(result, list)


def test_transaction_promotion_flow_get_eligible_promotions_is_active_at_transaction_time(
    ctx, seed: int = 42
):
    """
    Integration contract: every returned promotion must be active at the
    timestamp we passed in.  This validates that get_eligible_promotions()
    correctly filters promotions_df by date — a join between two subsystems.
    """
    rng = random.Random(seed)
    promo = _build_promotion(ctx, rng)
    transaction_time = fake.date_time_between(
        start_date=promo["effective_start_date"], end_date=promo["effective_end_date"]
    )
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    cart_subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
    result = get_eligible_promotions(ctx, transaction_time, cart_items, cart_subtotal)

    df = ctx.promotions.promotions_df
    for p in result:
        row = df[df["promotion_id"] == p["promotion_id"]].iloc[0]
        assert row["effective_start_date"] <= transaction_time
        assert row["effective_end_date"] >= transaction_time


def test_transaction_promotion_flow_get_eligible_promotions_filters_min_spend(
    ctx,
):
    """
    Integration contract: promotions whose minimum spend exceeds the cart
    subtotal must not be returned by get_eligible_promotions().
    """
    promotions_df = ctx.promotions.promotions_df

    candidates = promotions_df[promotions_df["min_spend"] > 0]
    if candidates.empty:
        pytest.skip("No promotions with a minimum spend requirement")

    promo = candidates.sort_values("min_spend", ascending=False).iloc[0]

    cart_items = [
        {
            "product_id": "TEST_PRODUCT",
            "name": "Test Product",
            "price": max(float(promo["min_spend"]) - 1, 0.01),
            "category": "TEST_CATEGORY",
            "quantity": 1,
        }
    ]

    cart_subtotal = cart_items[0]["price"]
    transaction_time = promo["effective_start_date"]

    result = get_eligible_promotions(
        ctx,
        transaction_time,
        cart_items,
        cart_subtotal,
    )

    promo_ids = {p["promotion_id"] for p in result}
    assert promo["promotion_id"] not in promo_ids


def test_transaction_promotion_flow_get_eligible_promotions_sorted_by_priority_descending(
    ctx,
    seed: int = 42,
):
    """
    Integration contract: eligible promotions should be returned in
    descending priority order.
    """
    rng = random.Random(seed)
    promo1, promo2 = _build_two_compatible_promotions(ctx, rng)
    cart1 = _build_cart_items_for_promotion(ctx, promo1, rng)
    cart2 = _build_cart_items_for_promotion(ctx, promo2, rng)

    if cart1 is None or cart2 is None:
        pytest.skip("Could not build valid carts")

    cart_items = cart1 + cart2

    cart_subtotal = sum(item["price"] * item["quantity"] for item in cart_items)

    start = max(
        promo1["effective_start_date"],
        promo2["effective_start_date"],
    )

    end = min(
        promo1["effective_end_date"],
        promo2["effective_end_date"],
    )

    if start > end:
        pytest.skip("Promotions do not overlap")

    transaction_time = fake.date_time_between(
        start_date=start,
        end_date=end,
    )

    result = get_eligible_promotions(
        ctx,
        transaction_time,
        cart_items,
        cart_subtotal,
    )

    if len(result) < 2:
        pytest.skip("Need multiple eligible promotions to validate ordering")

    priorities = [p["priority"] for p in result]
    assert priorities == sorted(priorities, reverse=True)


def test_transaction_promotion_flow_get_eligible_promotions_matches_cart_scope(
    ctx, seed: int = 42
):
    """
    Integration contract: every returned promotion must actually apply to
    something in the cart we submitted.  Tests that scope-matching logic
    correctly reads product/category/bundle data from ctx.
    """
    rng = random.Random(seed)
    promo = _build_promotion(ctx, rng)
    transaction_time = fake.date_time_between(
        start_date=promo["effective_start_date"], end_date=promo["effective_end_date"]
    )
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    cart_subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
    result = get_eligible_promotions(ctx, transaction_time, cart_items, cart_subtotal)

    cart_product_ids = {i["product_id"] for i in cart_items}
    cart_categories = {i["category"] for i in cart_items}
    bundle_dict = ctx.bundles.bundle_dict

    for p in result:
        scope = p["promotion_scope"]
        target = p["promotion_target_id"]

        if scope == "product":
            assert target in cart_product_ids, (
                f"Promotion {p['promotion_id']} targets product {target} "
                f"but it's not in the cart {cart_product_ids}"
            )
        elif scope == "category":
            assert target in cart_categories, (
                f"Promotion {p['promotion_id']} targets category {target} "
                f"but cart categories are {cart_categories}"
            )
        elif scope == "bundle":
            required = bundle_dict.get(target, {})
            cart_map = {i["product_id"]: i["quantity"] for i in cart_items}
            for pid, qty in required.items():
                assert cart_map.get(pid, 0) >= qty, (
                    f"Bundle {target} requires {qty}x {pid} but cart has "
                    f"{cart_map.get(pid, 0)}"
                )


def test_transaction_promotion_flow_get_eligible_promotions_expired_promotion_not_returned(
    ctx, seed: int = 42
):
    """
    Integration contract: a promotion whose window has closed must never
    appear in the eligible set, even if its scope matches the cart.
    """
    rng = random.Random(seed)
    promo = _build_promotion(ctx, rng)
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)

    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    cart_subtotal = sum(i["price"] * i["quantity"] for i in cart_items)

    # Use a timestamp outside of promotion effective windows
    df = ctx.promotions.promotions_df
    past_transaction_time = df["effective_start_date"].min() - pd.Timedelta(days=365)
    result = get_eligible_promotions(
        ctx, past_transaction_time, cart_items, cart_subtotal
    )

    assert (
        result == []
    ), "Expected no eligible promotions for a timestamp before all promo effective windows"


# ============================================================
# apply_cart_level_discount()
# ============================================================
# Integration contract: uses bundle + promotion data


def test_transaction_promotion_flow_apply_cart_level_discount_non_negative(
    ctx, seed: int = 42
):
    """
    Integration contract: discount must never be negative regardless of
    which promotion is applied against which cart.
    """
    rng = random.Random(seed)
    promo = _build_promotion(ctx, rng)
    promotion_id = promo["promotion_id"]
    transaction_time = fake.date_time_between(
        start_date=promo["effective_start_date"], end_date=promo["effective_end_date"]
    )
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    discount, _ = apply_cart_level_discount(
        ctx, cart_items, promotion_id, transaction_time
    )
    assert (
        discount >= 0
    ), f"Promotion {promo['promotion_id']} produced negative discount {discount}"


def test_transaction_promotion_flow_apply_cart_level_discount_unknown_promotion_returns_zero(
    ctx,
):
    """
    Integration contract: an unknown promotion id should never generate a
    discount or allocation.
    """
    cart_items = [
        {
            "product_id": "TEST_PRODUCT",
            "price": 10.0,
            "quantity": 2,
            "category": "TEST_CATEGORY",
        }
    ]

    discount, allocation = apply_cart_level_discount(
        ctx,
        cart_items,
        "PROMO_DOES_NOT_EXIST",
        pd.Timestamp("2025-01-01"),
    )

    assert discount == 0
    assert allocation == {}


def test_transaction_promotion_flow_apply_cart_level_discount_expired_promotion_returns_zero(
    ctx,
    seed: int = 42,
):
    """
    Integration contract: a promotion outside its effective date window
    must not generate a discount.
    """
    rng = random.Random(seed)
    promo = _build_non_shipping_promotion(ctx)
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)

    if cart_items is None:
        pytest.skip("Could not build a valid cart")

    transaction_time = pd.Timestamp(promo["effective_start_date"]) - pd.Timedelta(
        days=365
    )

    discount, _ = apply_cart_level_discount(
        ctx,
        cart_items,
        promo["promotion_id"],
        transaction_time,
    )

    assert discount == 0


def test_transaction_promotion_flow_apply_cart_level_discount_allocation_proportional_to_item_value(
    ctx,
    seed: int = 42,
):
    """
    Integration contract: proportional allocation should assign a larger
    discount share to higher-value eligible items.
    """
    rng = random.Random(seed)
    promo = _build_non_shipping_promotion(ctx)
    transaction_time = fake.date_time_between(
        start_date=promo["effective_start_date"],
        end_date=promo["effective_end_date"],
    )

    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
    if cart_items is None or len(cart_items) < 2:
        pytest.skip("Need at least two cart items")

    discount, allocation = apply_cart_level_discount(
        ctx,
        cart_items,
        promo["promotion_id"],
        transaction_time,
    )

    if discount == 0 or len(allocation) < 2:
        pytest.skip("Promotion not applicable for proportional allocation check")

    subtotals = {
        item["product_id"]: item["price"] * item["quantity"] for item in cart_items
    }

    ranked_subtotals = sorted(subtotals.items(), key=lambda x: x[1], reverse=True)
    high_pid, _ = ranked_subtotals[0]
    low_pid, _ = ranked_subtotals[-1]

    if high_pid in allocation and low_pid in allocation:
        assert allocation[high_pid] >= allocation[low_pid]


def test_transaction_promotion_flow_apply_cart_level_discount_does_not_exceed_cart_subtotal(
    ctx, seed: int = 42
):
    """
    Integration contract: discount must never exceed the value of the
    eligible items.  Validates that is_promotion_viable() + allocation
    logic work together correctly.
    """
    rng = random.Random(seed)
    promo = _build_promotion(ctx, rng)
    promotion_id = promo["promotion_id"]
    transaction_time = fake.date_time_between(
        start_date=pd.Timestamp(promo["effective_start_date"]),
        end_date=pd.Timestamp(promo["effective_end_date"]),
    )
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    discount, _ = apply_cart_level_discount(
        ctx, cart_items, promotion_id, transaction_time
    )
    cart_subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
    assert discount <= cart_subtotal + 0.01, (
        f"Discount {discount} exceeds cart subtotal {cart_subtotal} "
        f"for promotion {promo['promotion_id']}"
    )


def test_transaction_promotion_flow_apply_cart_level_discount_allocations_sums_to_discount(
    ctx, seed: int = 42
):
    """
    Integration contract: the per-item allocation dict must sum to the
    total discount.  This is the key invariant that the transaction
    generator relies on for total reconciliation.
    """
    rng = random.Random(seed)
    promo = _build_non_shipping_promotion(ctx)
    promotion_id = promo["promotion_id"]
    transaction_time = fake.date_time_between(
        start_date=promo["effective_start_date"], end_date=promo["effective_end_date"]
    )
    cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    discount, allocation = apply_cart_level_discount(
        ctx, cart_items, promotion_id, transaction_time
    )

    if discount == 0:
        pytest.skip(
            f"Promotion {promotion_id} not applicable for this cart/time window; "
            "allocation-to-discount consistency not testable."
        )

    allocation_total = sum(allocation.values())
    assert abs(allocation_total - discount) < 0.02, (
        f"Allocation sum {allocation_total:.4f} != discount {discount:.4f} "
        f"for promotion {promo['promotion_id']}"
    )


def test_transaction_promotion_flow_apply_cart_level_discount_bundle_discount_uses_active_bundle_pricing(
    ctx, seed: int = 42
):
    """
    Integration contract: bundle promotions must compute discount from the
    bundle_pricings_df row that is active at the transaction timestamp —
    not from a hardcoded value.  Tests that get_active_bundle_pricing()
    output feeds correctly into apply_cart_level_discount().
    """
    rng = random.Random(seed)
    bundle_promo = _build_bundle_promotion(ctx)
    if bundle_promo is None:
        pytest.skip("No bundle promotions in generated data")

    promotion_id = bundle_promo["promotion_id"]
    bundle_id = bundle_promo["promotion_target_id"]
    transaction_time = fake.date_time_between(
        start_date=bundle_promo["effective_start_date"],
        end_date=bundle_promo["effective_end_date"],
    )
    cart_items = _build_cart_items_for_promotion(ctx, bundle_promo, rng)
    if cart_items is None:
        pytest.skip("Could not build a valid cart for this promotion scope")

    # Get the pricing directly
    pricing = get_active_bundle_pricing(ctx, bundle_id, transaction_time)

    if pricing is None:
        pytest.skip("No active bundle pricing at this timestamp")

    cart_subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
    discount, _ = apply_cart_level_discount(
        ctx, cart_items, promotion_id, transaction_time
    )
    expected_discount = max(cart_subtotal - pricing["bundle_price"], 0)

    assert abs(discount - expected_discount) < 0.02, (
        f"Bundle discount {discount:.4f} does not match "
        f"expected {expected_discount:.4f} from active pricing"
    )


# ============================================================
# resolve_promotion_stack()
# ============================================================
# Integration contract: uses promotion data


def test_transaction_promotion_flow_resolve_promotion_stack_no_conflicting_promotions_all_selected(
    ctx, seed: int = 42
):
    """
    Integration contract: when promotions target completely different
    products/categories with no overlap, all of them should be selected.
    """
    rng = random.Random(seed)

    p1 = {
        "promotion_id": "PROMO001",
        "promotion_scope": "product",
        "promotion_target_id": "PROD001",
        "priority": 3,
    }

    p2 = {
        "promotion_id": "PROMO002",
        "promotion_scope": "product",
        "promotion_target_id": "PROD002",
        "priority": 3,
    }

    promotions = [p1, p2]
    transaction_time = _build_datetime()
    customer_segment = _build_customer_segment()
    cart_items = [
        {
            "product_id": "PROD001",
            "price": rng.randint(1, 30),
            "quantity": rng.randint(1, 3),
            "category": "CATEGORY_A",
        },
        {
            "product_id": "PROD002",
            "price": rng.randint(1, 30),
            "quantity": rng.randint(1, 3),
            "category": "CATEGORY_B",
        },
    ]

    cart_subtotal = sum(
        cast(float, i["price"]) * cast(int, i["quantity"]) for i in cart_items
    )

    result = resolve_promotion_stack(
        ctx,
        customer_segment,
        promotions,
        cart_items,
        transaction_time,
        cart_subtotal,
        transaction_type="In Store",
    )

    selected_ids = {p["promotion_id"] for p in result}
    assert p1["promotion_id"] in selected_ids
    assert p2["promotion_id"] in selected_ids


def test_transaction_promotion_flow_resolve_promotion_stack_conflicting_promotions_best_one_wins(
    ctx, seed: int = 42
):
    """
    Integration contract: when two promotions target the same product,
    resolve_promotion_stack() must keep exactly one — the one that
    produces the larger discount.  This tests the is_overlap() +
    apply_cart_level_discount() comparison logic working together.
    """
    rng = random.Random(seed)

    p1 = {
        "promotion_id": "PROMO001",
        "promotion_scope": "product",
        "promotion_target_id": "PROD001",
        "priority": 3,
    }

    p2 = {
        "promotion_id": "PROMO002",
        "promotion_scope": "product",
        "promotion_target_id": "PROD001",
        "priority": 3,
    }

    promotions = [p1, p2]
    transaction_time = _build_datetime()
    customer_segment = _build_customer_segment()
    cart_items = [
        {
            "product_id": "PROD001",
            "price": rng.randint(1, 30),
            "quantity": rng.randint(1, 3),
            "category": "CATEGORY_A",
        },
    ]

    cart_subtotal = sum(
        cast(float, i["price"]) * cast(int, i["quantity"]) for i in cart_items
    )

    result = resolve_promotion_stack(
        ctx,
        customer_segment,
        promotions,
        cart_items,
        transaction_time,
        cart_subtotal,
        transaction_type="In Store",
    )

    # Exactly one promotion survives
    assert (
        len(result) == 1
    ), f"Expected 1 promotion after conflict resolution, got {len(result)}"

    # The surviving one produces >= discount than the other
    winner_id = result[0]["promotion_id"]
    winner_discount, _ = apply_cart_level_discount(
        ctx, cart_items, winner_id, transaction_time
    )
    loser_id = (
        p1["promotion_id"] if winner_id == p2["promotion_id"] else p2["promotion_id"]
    )
    loser_discount, _ = apply_cart_level_discount(
        ctx, cart_items, loser_id, transaction_time
    )

    assert (
        winner_discount >= loser_discount
    ), f"Winner discount {winner_discount:.4f} < loser discount {loser_discount:.4f}"
