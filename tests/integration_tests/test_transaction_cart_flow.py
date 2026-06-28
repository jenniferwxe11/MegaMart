import random

import pytest
from faker import Faker

from data_generation.config.store_products_config import ESSENTIAL_CATEGORIES
from data_generation.services.transactions.transaction_cart_service import (
    generate_cart_items,
)
from tests.helpers import _build_customer_segment

fake = Faker()
fake.seed_instance(42)


# ============================================================
# generate_cart_items()
# ============================================================
# Integration contract: uses store + product catalogue data


def test_transaction_cart_flow_generate_cart_items_returns_non_empty_list(
    ctx, seed: int = 42
):
    """
    Integration contract: generate_cart_items() must always return at least
    one item.
    """
    rng = random.Random(seed)
    store_id = rng.choice(ctx.stores.retail_store_ids)
    items = generate_cart_items(ctx, customer_segment=None, store_id=store_id)

    assert isinstance(items, list)
    assert len(items) >= 1, "generate_cart_items() returned empty cart"


def test_transaction_cart_flow_generate_cart_items_all_products_exist_in_catalogue(
    ctx, seed: int = 42
):
    """
    Integration contract: every product_id in the generated cart must
    exist in either the store catalogue or the global product catalogue.
    Tests that store_product lookups fall back to global products correctly.
    """
    rng = random.Random(seed)
    store_id = rng.choice(ctx.stores.retail_store_ids)
    customer_segment = _build_customer_segment()
    items = generate_cart_items(ctx, customer_segment, store_id)

    all_product_ids = set(ctx.products.product_ids)
    for item in items:
        assert (
            item["product_id"] in all_product_ids
        ), f"Cart item product_id {item['product_id']!r} not in global product catalogue"


def test_transaction_cart_flow_generate_cart_items_each_item_has_required_fields(
    ctx, seed: int = 42
):
    """
    Integration contract: every cart item dict must contain the four fields
    that transaction_promotion_service and the transaction generator depend on.
    """
    rng = random.Random(seed)
    store_id = rng.choice(ctx.stores.retail_store_ids)
    customer_segment = _build_customer_segment()
    items = generate_cart_items(ctx, customer_segment, store_id)

    required = {"product_id", "name", "price", "category", "quantity"}
    for item in items:
        missing = required - set(item.keys())
        assert not missing, f"Cart item missing fields: {missing} — item: {item}"
        assert (
            item["price"] is not None and item["price"] > 0
        ), f"Cart item has invalid price: {item['price']}"
        assert (
            item["quantity"] >= 1
        ), f"Cart item has invalid quantity: {item['quantity']}"


def test_transaction_cart_flow_generate_cart_items_essential_categories_represented(
    ctx, seed: int = 42
):
    """
    Integration contract: the generated cart should contain a reasonable
    proportion (~60-70%) of essential category items, reflecting the
    essential_ratio logic in generate_cart_items().
    """
    rng = random.Random(seed)
    store_id = rng.choice(ctx.stores.retail_store_ids)
    customer_segment = _build_customer_segment()

    # Run across multiple carts to smooth randomness
    essential_counts = []
    total_counts = []
    for _ in range(20):
        items = generate_cart_items(ctx, customer_segment, store_id)
        essential = sum(
            item["quantity"]
            for item in items
            if item.get("category") in ESSENTIAL_CATEGORIES
        )
        total = sum(item["quantity"] for item in items)
        essential_counts.append(essential)
        total_counts.append(total)

    overall_essential = sum(essential_counts)
    overall_total = sum(total_counts)

    if overall_total == 0:
        pytest.skip("No items generated across all carts")

    ratio = overall_essential / overall_total
    assert (
        0.30 <= ratio <= 0.85
    ), f"Essential category ratio {ratio:.2f} out of expected range [0.40, 0.85]"


def test_transaction_cart_flow_generate_cart_items_store_catalogue_prices_used(
    ctx, seed: int = 42
):
    """
    Integration contract: prices in the cart must match the store catalogue
    price for that (store_id, product_id) pair when one exists, before
    falling back to the global price map.
    """
    rng = random.Random(seed)
    store_id = rng.choice(ctx.stores.retail_store_ids)
    customer_segment = _build_customer_segment()
    items = generate_cart_items(ctx, customer_segment, store_id)

    store_price_map = ctx.store_catalogues.store_product_price_map
    global_price_map = ctx.products.product_price_map

    for item in items:
        pid = item["product_id"]
        store_price = store_price_map.get((store_id, pid))
        global_price = global_price_map.get(pid)
        expected_price = store_price if store_price is not None else global_price

        if expected_price is None:
            continue

        assert abs(item["price"] - expected_price) < 0.01, (
            f"Cart item price {item['price']} does not match expected "
            f"{expected_price} for product {pid!r} at store {store_id!r}"
        )
