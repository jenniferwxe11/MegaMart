import random

from faker import Faker

from data_generation.config.products_config import CATEGORY_AFFINITY
from data_generation.config.promotions_config import (
    DOLLAR_DISCOUNT_MAX_RATIO,
    PERCENTAGE_DISCOUNT_MAX_PCT,
)
from data_generation.services.transactions.transaction_cart_service import (
    sample_products,
)
from data_generation.services.transactions.transaction_promotion_service import (
    is_bundle_valid,
    is_overlap,
    is_promotion_viable,
    select_shipping_promo,
    should_use_promo,
)
from tests.helpers import (
    _build_bundle,
    _build_category,
    _build_category_product_id,
    _build_customer_segment,
    _build_insufficient_quantity_bundle_cart,
    _build_promotion,
    _build_valid_bundle_cart,
)

fake = Faker()


# ============================================================
# sample_products()
# ============================================================
# UNIT: needs product_ctx only to resolve category→product_ids.
# The selection logic (affinity clustering) is what we are testing.


def test_transaction_sample_products(product_ctx):
    (category,) = _build_category(product_ctx, 1)
    product_id = _build_category_product_id(product_ctx, category)
    affinity_categories = set(CATEGORY_AFFINITY.get(category, []))
    affinity_categories.add(category)

    result = sample_products(product_ctx, [product_id], 10)
    assert len(result) == 10

    product_category_map = product_ctx.products.product_category_map
    for pid in result:
        assert pid in product_category_map
        pid_category = product_category_map.get(pid)

        if CATEGORY_AFFINITY.get(category):
            assert pid_category in affinity_categories


# ============================================================
# is_bundle_valid()
# ============================================================
# UNIT: bundle_dict is the only ctx field read. We use the bundle_ctx
# fixture purely to resolve a real bundle_id → required items dict,
# then test the cart-matching logic in isolation.


def test_transaction_is_bundle_valid_returns_true(bundle_ctx):
    bundle = _build_bundle(bundle_ctx)
    bundle_id = bundle["bundle_id"]

    # Add bundle items into cart
    cart_items = _build_valid_bundle_cart(bundle_ctx, bundle_id)

    result = is_bundle_valid(bundle_ctx, bundle_id, cart_items)
    assert result


def test_transaction_is_bundle_valid_returns_false(bundle_ctx):
    bundle = _build_bundle(bundle_ctx)
    bundle_id = bundle["bundle_id"]

    # Add bundle items into cart with insufficient quantity
    cart_items = _build_insufficient_quantity_bundle_cart(bundle_ctx, bundle_id)

    result = is_bundle_valid(bundle_ctx, bundle_id, cart_items)
    assert not result


# ============================================================
# select_shipping_promo()
# ============================================================


def test_transaction_select_shipping_promo_empty_promotions():
    result = select_shipping_promo([], 100)
    assert result is None


def test_transaction_select_shipping_promo_no_free_shipping():
    promotions = [{"promotion_mechanic": "dollar_discount"}]
    result = select_shipping_promo(promotions, 100)
    assert result is None


def test_transaction_select_shipping_promo_no_eligible_free_shipping():
    promotions = [{"promotion_mechanic": "free_shipping", "min_spend": 200}]
    result = select_shipping_promo(promotions, 100)
    assert result is None


def test_transaction_select_shipping_promo_has_eligible_free_shipping():
    promotions = [
        {"promotion_mechanic": "free_shipping", "min_spend": 50},
        {"promotion_mechanic": "free_shipping", "min_spend": 30},
    ]
    result = select_shipping_promo(promotions, 100)

    # Expected best promo = lowest min_spend
    expected = min(
        promotions,
        key=lambda x: float("inf") if x.get("min_spend") is None else x["min_spend"],
    )
    assert result == expected


# ============================================================
# is_overlap()
# ============================================================
# UNIT: only bundle_dict is read from ctx.  All scope logic is tested
# with plain dicts. Bundle-vs-product and bundle-vs-bundle cases use
# bundle_ctx to resolve real bundle contents — the function logic is
# what is under test, not the data itself.


def test_transaction_is_overlap_product_product_overlap(bundle_ctx):
    promo_a = {"promotion_scope": "product", "promotion_target_id": "PROD001"}
    promo_b = {"promotion_scope": "product", "promotion_target_id": "PROD001"}
    assert is_overlap(bundle_ctx, promo_a, promo_b, [])


def test_transaction_is_overlap_product_product_no_overlap(bundle_ctx):
    promo_a = {"promotion_scope": "product", "promotion_target_id": "PROD001"}
    promo_b = {"promotion_scope": "product", "promotion_target_id": "PROD002"}
    assert not is_overlap(bundle_ctx, promo_a, promo_b, [])


def test_transaction_is_overlap_category_category_overlap(bundle_ctx):
    promo_a = {"promotion_scope": "category", "promotion_target_id": "CATEGORY_A"}
    promo_b = {"promotion_scope": "category", "promotion_target_id": "CATEGORY_A"}
    assert is_overlap(bundle_ctx, promo_a, promo_b, [])


def test_transaction_is_overlap_category_category_no_overlap(bundle_ctx):
    promo_a = {"promotion_scope": "category", "promotion_target_id": "CATEGORY_A"}
    promo_b = {"promotion_scope": "category", "promotion_target_id": "CATEGORY_B"}
    assert not is_overlap(bundle_ctx, promo_a, promo_b, [])


def test_transaction_is_overlap_product_category_overlap(bundle_ctx):
    promo_a = {"promotion_scope": "product", "promotion_target_id": "PROD001"}
    promo_b = {"promotion_scope": "category", "promotion_target_id": "CATEGORY_A"}
    cart_items = [{"product_id": "PROD001", "category": "CATEGORY_A"}]
    assert is_overlap(bundle_ctx, promo_a, promo_b, cart_items)


def test_transaction_is_overlap_product_category_no_overlap(bundle_ctx):
    promo_a = {"promotion_scope": "product", "promotion_target_id": "PROD001"}
    promo_b = {"promotion_scope": "category", "promotion_target_id": "CATEGORY_B"}
    cart_items = [{"product_id": "PROD001", "category": "CATEGORY_A"}]
    assert not is_overlap(bundle_ctx, promo_a, promo_b, cart_items)


def test_transaction_is_overlap_bundle_product_overlap(bundle_ctx, seed: int = 42):
    rng = random.Random(seed)
    bundle_dict = bundle_ctx.bundles.bundle_dict
    bundle_id = rng.choice(list(bundle_dict))
    bundle_items = bundle_dict[bundle_id]
    product_id = rng.choice(list(bundle_items))
    promo_a = {"promotion_scope": "bundle", "promotion_target_id": bundle_id}
    promo_b = {"promotion_scope": "product", "promotion_target_id": product_id}
    assert is_overlap(bundle_ctx, promo_a, promo_b, [])


def test_transaction_is_overlap_bundle_product_no_overlap(bundle_ctx, seed: int = 42):
    rng = random.Random(seed)
    bundle_dict = bundle_ctx.bundles.bundle_dict
    bundle_id = rng.choice(list(bundle_dict))
    bundle_items = bundle_dict[bundle_id]
    bundle_product_ids = set(bundle_items)
    all_product_ids = set(bundle_ctx.products.product_ids)
    non_bundle_products_ids = list(all_product_ids - bundle_product_ids)
    product_id = rng.choice(non_bundle_products_ids)
    promo_a = {"promotion_scope": "bundle", "promotion_target_id": bundle_id}
    promo_b = {"promotion_scope": "product", "promotion_target_id": product_id}
    assert not is_overlap(bundle_ctx, promo_a, promo_b, [])


def test_transaction_is_overlap_bundle_bundle_overlap(bundle_ctx):
    bundle = _build_bundle(bundle_ctx)
    b1 = b2 = bundle["bundle_id"]
    promo_a = {"promotion_scope": "bundle", "promotion_target_id": b1}
    promo_b = {"promotion_scope": "bundle", "promotion_target_id": b2}
    assert is_overlap(bundle_ctx, promo_a, promo_b, [])


def test_transaction_is_overlap_bundle_bundle_no_overlap(bundle_ctx):
    bundle_dict = bundle_ctx.bundles.bundle_dict
    keys = list(bundle_dict.keys())
    b1, b2 = keys[0], keys[-1]
    promo_a = {"promotion_scope": "bundle", "promotion_target_id": b1}
    promo_b = {"promotion_scope": "bundle", "promotion_target_id": b2}
    assert not is_overlap(bundle_ctx, promo_a, promo_b, [])


# ============================================================
# should_use_promo()
# ============================================================


def test_transaction_should_use_promo(seed: int = 42):
    rng = random.Random(seed)
    customer_segment = _build_customer_segment()
    cart_subtotal = rng.randint(10, 500)
    result = should_use_promo(customer_segment, cart_subtotal)
    assert 0 <= result <= 1


# ============================================================
# is_promotion_viable()
# ============================================================


def test_transaction_is_promotion_viable_empty_items(promotion_ctx, seed: int = 42):
    # UNIT: promotion_ctx used only to get a realistic promo dict shape;
    # the function itself does not read ctx.
    rng = random.Random(seed)
    promotion = _build_promotion(promotion_ctx, rng)
    result = is_promotion_viable(promotion, [])
    assert not result


def test_transaction_is_promotion_viable_category_scope_dollar_discount_exceeds(
    seed: int = 42,
):
    rng = random.Random(seed)
    items = [{"price": 50, "quantity": 2}]
    item_subtotal = items[0]["price"] * items[0]["quantity"]
    promotion_value = item_subtotal * rng.uniform(DOLLAR_DISCOUNT_MAX_RATIO + 0.01, 1)
    promotion = {
        "promotion_mechanic": "dollar_discount",
        "promotion_scope": "category",
        "promotion_value": promotion_value,
    }
    result = is_promotion_viable(promotion, items)
    assert not result


def test_transaction_is_promotion_viable_category_scope_dollar_discount_does_not_exceed(
    seed: int = 42,
):
    rng = random.Random(seed)
    items = [{"price": 50, "quantity": 2}]
    item_subtotal = items[0]["price"] * items[0]["quantity"]
    promotion_value = item_subtotal * rng.uniform(0, DOLLAR_DISCOUNT_MAX_RATIO)
    promotion = {
        "promotion_mechanic": "dollar_discount",
        "promotion_scope": "category",
        "promotion_value": promotion_value,
    }
    result = is_promotion_viable(promotion, items)
    assert result


def test_transaction_is_promotion_viable_product_scope_dollar_discount_exceeds(
    seed: int = 42,
):
    rng = random.Random(seed)
    items = [{"price": 50, "quantity": 1}]
    promotion_value = items[0]["price"] * rng.uniform(
        DOLLAR_DISCOUNT_MAX_RATIO + 0.01, 1
    )
    promotion = {
        "promotion_mechanic": "dollar_discount",
        "promotion_scope": "product",
        "promotion_value": promotion_value,
    }
    result = is_promotion_viable(promotion, items)
    assert not result


def test_transaction_is_promotion_viable_product_scope_dollar_discount_does_not_exceed(
    seed: int = 42,
):
    rng = random.Random(seed)
    items = [{"price": 50, "quantity": 1}]
    promotion_value = items[0]["price"] * rng.uniform(0, DOLLAR_DISCOUNT_MAX_RATIO)
    promotion = {
        "promotion_mechanic": "dollar_discount",
        "promotion_scope": "product",
        "promotion_value": promotion_value,
    }
    result = is_promotion_viable(promotion, items)
    assert result


def test_transaction_is_promotion_viable_product_scope_percentage_discount_exceeds(
    seed: int = 42,
):
    rng = random.Random(seed)
    items = [{"price": 50, "quantity": 1}]
    promotion_value = rng.uniform(PERCENTAGE_DISCOUNT_MAX_PCT + 1, 100)
    promotion = {
        "promotion_mechanic": "percentage_discount",
        "promotion_scope": "product",
        "promotion_value": promotion_value,
    }
    result = is_promotion_viable(promotion, items)
    assert not result


def test_transaction_is_promotion_viable_product_scope_percentage_discount_does_not_exceed(
    seed: int = 42,
):
    rng = random.Random(seed)
    items = [{"price": 50, "quantity": 1}]
    promotion_value = rng.uniform(0, PERCENTAGE_DISCOUNT_MAX_PCT)
    promotion = {
        "promotion_mechanic": "percentage_discount",
        "promotion_scope": "product",
        "promotion_value": promotion_value,
    }
    result = is_promotion_viable(promotion, items)
    assert result
