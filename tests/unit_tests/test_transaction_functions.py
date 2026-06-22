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
from data_generation.services.transactions.transaction_lookup_service import (
    get_active_bundle_pricing,
    get_shipping_fee,
    get_store,
)
from data_generation.services.transactions.transaction_promotion_service import (
    is_bundle_valid,
    is_overlap,
    is_promotion_viable,
    opt_for_delivery,
    select_shipping_promo,
    should_use_promo,
)
from tests.unit_tests.helpers import (
    _build_bundle,
    _build_category,
    _build_customer,
    _build_customer_segment,
    _build_insufficient_quantity_bundle_cart,
    _build_product,
    _build_promotion,
    _build_valid_bundle_cart,
)

fake = Faker()


# ============================================================
# sample_products()
# ============================================================


def test_transaction_sample_products(product_ctx):
    (category,) = _build_category(product_ctx, 1)
    product_id = _build_product(product_ctx, category)
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
# get_store()
# ============================================================


def test_transaction_get_store(customer_store_ctx):
    customer = _build_customer(customer_store_ctx)
    customer_id = customer["customer_id"]
    cust_area = customer["area"]
    result = get_store(customer_store_ctx, customer_id)
    stores_df = customer_store_ctx.stores.stores_df
    candidates = stores_df[stores_df["area"] == cust_area]["store_id"].tolist()

    if candidates:
        assert result in candidates
    else:
        assert result in customer_store_ctx.stores.retail_store_ids


# ============================================================
# get_shipping_fee()
# ============================================================


def test_transaction_get_shipping_fee(customer_store_ctx, seed: int = 42):
    rng = random.Random(seed)
    customer = _build_customer(customer_store_ctx)
    customer_id = customer["customer_id"]
    store_id = rng.choice(customer_store_ctx.stores.store_ids)
    result = get_shipping_fee(customer_store_ctx, store_id, customer_id)

    cust_area = customer["area"]
    cust_region = customer["region"]
    store_area = customer_store_ctx.stores.store_area_map[store_id]
    store_region = customer_store_ctx.stores.store_region_map[store_id]
    online_store_id = customer_store_ctx.stores.online_store_id

    # Recompute base fee deterministically
    if store_id == online_store_id:
        base_fee = 8
    else:
        base_fee = 4

    if cust_region != store_region:
        base_fee += 8
    elif cust_area != store_area:
        base_fee += 4

    assert base_fee <= result <= base_fee + 2


# ============================================================
# get_active_bundle_pricing()
# ============================================================


def test_transaction_get_active_bundle_pricing(bundle_ctx):
    bundle = _build_bundle(bundle_ctx)
    bundle_id = bundle["bundle_id"]
    df = bundle_ctx.bundles.bundle_pricings_df
    row = df[df["bundle_id"] == bundle_id].sample(1).iloc[0]
    transaction_date = row["effective_start_date"]

    result = get_active_bundle_pricing(bundle_ctx, bundle_id, transaction_date)
    if result is None:
        # Ensure truly no valid rows exist
        valid = df[
            (df["bundle_id"] == bundle_id)
            & (df["effective_start_date"] <= transaction_date)
            & (df["effective_end_date"] >= transaction_date)
        ]
        assert valid.empty
        return

    # Invariant checks
    assert result["bundle_id"] == bundle_id
    assert result["effective_start_date"] <= transaction_date
    assert result["effective_end_date"] >= transaction_date

    # Ensure it is actually the "best" row
    valid = df[
        (df["bundle_id"] == bundle_id)
        & (df["effective_start_date"] <= transaction_date)
        & (df["effective_end_date"] >= transaction_date)
    ]
    assert not valid.empty
    assert result["effective_start_date"] == valid["effective_start_date"].max()


# ============================================================
# is_bundle_valid()
# ============================================================


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
# opt_for_delivery()
# ============================================================


def test_transaction_opt_for_delivery(
    customer_store_ctx, promotion_ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer_id = rng.choice(customer_store_ctx.customers.customer_ids)
    store_id = rng.choice(customer_store_ctx.stores.store_ids)
    df = promotion_ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
    )
    shipping_promo = shipping_promo.to_dict() if shipping_promo is not None else None
    cart_subtotal = rng.randint(10, 500)
    result = opt_for_delivery(
        customer_store_ctx, customer_id, store_id, shipping_promo, cart_subtotal
    )
    assert isinstance(result, bool)
    assert result <= 85.0


def test_transaction_opt_for_delivery_free_shipping_increase_opt_in_rate(
    customer_store_ctx, promotion_ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer_id = rng.choice(customer_store_ctx.customers.customer_ids)
    store_id = rng.choice(customer_store_ctx.stores.store_ids)
    df = promotion_ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
    )
    shipping_promo = shipping_promo.to_dict() if shipping_promo is not None else None
    cart_subtotal = rng.randint(10, 500)
    result_no_free_shipping = sum(
        opt_for_delivery(customer_store_ctx, customer_id, store_id, None, cart_subtotal)
        for _ in range(100)
    )
    result_has_free_shipping = sum(
        opt_for_delivery(
            customer_store_ctx, customer_id, store_id, shipping_promo, cart_subtotal
        )
        for _ in range(100)
    )
    assert result_no_free_shipping < result_has_free_shipping


def test_transaction_opt_for_delivery_high_cart_value_increase_opt_in_rate(
    customer_store_ctx, promotion_ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer_id = rng.choice(customer_store_ctx.customers.customer_ids)
    store_id = rng.choice(customer_store_ctx.stores.store_ids)
    df = promotion_ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
    )
    shipping_promo = shipping_promo.to_dict() if shipping_promo is not None else None
    result_low_cart_value = sum(
        opt_for_delivery(customer_store_ctx, customer_id, store_id, shipping_promo, 20)
        for _ in range(100)
    )
    result_high_cart_value = sum(
        opt_for_delivery(customer_store_ctx, customer_id, store_id, shipping_promo, 200)
        for _ in range(100)
    )
    assert result_low_cart_value < result_high_cart_value


def test_transaction_opt_for_delivery_cross_region_increase_opt_in_rate(
    customer_store_ctx, promotion_ctx, seed: int = 42
):
    customer = {
        "customer_id": "CUST001",
        "region": "Central",
    }
    customer_id = customer["customer_id"]
    cust_region = customer["region"]
    df = customer_store_ctx.stores.stores_df
    store_1 = df[df["region"] == cust_region].sample(n=1, random_state=seed).iloc[0]
    store_2 = df[df["region"] != cust_region].sample(n=1, random_state=seed).iloc[0]
    df = promotion_ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
    )
    shipping_promo = shipping_promo.to_dict() if shipping_promo is not None else None
    result_same_region = sum(
        opt_for_delivery(
            customer_store_ctx, customer_id, store_1["store_id"], shipping_promo, 20
        )
        for _ in range(100)
    )
    result_cross_region = sum(
        opt_for_delivery(
            customer_store_ctx, customer_id, store_2["store_id"], shipping_promo, 200
        )
        for _ in range(100)
    )
    assert result_same_region < result_cross_region


# ============================================================
# is_promotion_viable()
# ============================================================


def test_transaction_is_promotion_viable_empty_items(promotion_ctx):
    promotion = _build_promotion(promotion_ctx)
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
