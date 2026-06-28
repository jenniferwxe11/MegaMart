import random

from faker import Faker

from data_generation.services.transactions.transaction_promotion_service import (
    apply_cart_level_discount,
    get_eligible_promotions,
    resolve_promotion_stack,
)
from tests.helpers import (
    _build_cart_items_for_promotion,
    _build_customer_segment,
    _build_promotion,
)

fake = Faker()
fake.seed_instance(42)


# ============================================================
# Full pipeline
# ============================================================


def test_transaction_pipeline_flow_full_pipeline(ctx, seed: int = 42):
    """
    Integration contract: the end to end pipeline must produce item level
    discounts that sum to the transaction level total_discount.
    This is the reconciliation invariant that the transaction generator
    enforces with a drift correction step — we verify it holds BEFORE that
    correction for well formed carts.

    Flow tested:
        cart → get_eligible_promotions()
            → resolve_promotion_stack()
            → apply_cart_level_discount() × N
            → sum(item_discounts) ≈ total_discount
    """
    rng = random.Random(seed)

    N = 20

    passed = 0
    for _ in range(N):
        promo = _build_promotion(ctx, rng)
        cart_items = _build_cart_items_for_promotion(ctx, promo, rng)
        customer_segment = _build_customer_segment()

        if cart_items is None:
            continue

        transaction_time = fake.date_time_between(
            start_date=promo["effective_start_date"],
            end_date=promo["effective_end_date"],
        )
        cart_subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
        eligible = get_eligible_promotions(
            ctx, transaction_time, cart_items, cart_subtotal
        )
        non_shipping_promo = [
            p for p in eligible if p["promotion_mechanic"] != "free_shipping"
        ]
        stacked = resolve_promotion_stack(
            ctx,
            customer_segment,
            non_shipping_promo,
            cart_items,
            transaction_time,
            cart_subtotal,
            transaction_type="In Store",
        )

        total_discount = 0
        final_allocation: dict = {}

        for p in stacked:
            discount, allocation = apply_cart_level_discount(
                ctx, cart_items, p["promotion_id"], transaction_time
            )
            total_discount += discount
            for k, v in allocation.items():
                final_allocation[k] = final_allocation.get(k, 0) + v

        if total_discount == 0:
            continue

        allocation_sum = sum(final_allocation.values())
        assert abs(allocation_sum - total_discount) < 0.05, (
            f"Allocation sum {allocation_sum:.4f} diverges from "
            f"total_discount {total_discount:.4f}"
        )
        passed += 1

    assert (
        passed >= 3
    ), "Could not build enough valid carts to run the reconciliation check"
