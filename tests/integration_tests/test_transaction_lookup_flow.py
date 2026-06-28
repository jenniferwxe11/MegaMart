import itertools
import random

import pytest
from faker import Faker

from data_generation.services.transactions.transaction_lookup_service import (
    get_active_bundle_pricing,
    get_shipping_fee,
    get_store,
)
from data_generation.services.transactions.transaction_promotion_service import (
    opt_for_delivery,
)
from tests.helpers import (
    _build_bundle,
    _build_customer,
    _build_customer_with_location,
)

fake = Faker()
fake.seed_instance(42)


# ============================================================
# get_store()
# ============================================================
# Integration contract: uses store + customer data


def test_transaction_lookup_flow_get_store(ctx):
    """
    Integration contract: get_store() must always return a store_id that
    exists in stores_df.  Tests that the location lookup correctly
    maps a real customer's area to a real store.
    """
    customer = _build_customer(ctx)
    customer_id = customer["customer_id"]
    cust_area = customer["area"]
    result = get_store(ctx, customer_id)
    stores_df = ctx.stores.stores_df
    candidates = stores_df[stores_df["area"] == cust_area]["store_id"].tolist()

    if candidates:
        assert result in candidates
    else:
        assert result in ctx.stores.retail_store_ids


# ============================================================
# get_shipping_fee()
# ============================================================
# Integration contract: uses store + customer data


def test_transaction_lookup_flow_get_shipping_fee_base_fee_calculation(
    ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer = _build_customer_with_location(ctx)
    customer_id = customer["customer_id"]
    cust_area = customer["area"]
    cust_region = customer["region"]

    store_id = rng.choice(ctx.stores.store_ids)
    store_area = ctx.stores.store_area_map[store_id]
    store_region = ctx.stores.store_region_map[store_id]
    online_store_id = ctx.stores.online_store_id

    result = get_shipping_fee(ctx, store_id, customer_id)

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


def test_transaction_lookup_flow_get_shipping_fee_reflects_distance(
    ctx, seed: int = 42
):
    """
    Integration contract: a customer shopping cross-region must pay a
    higher shipping fee than the same customer shopping in their home
    region.  Tests that get_shipping_fee() correctly joins customer area
    map → store area map → region comparison.
    """
    rng = random.Random(seed)
    customer = _build_customer_with_location(ctx)
    customer_id = customer["customer_id"]
    cust_region = customer["region"]

    stores_df = ctx.stores.stores_df
    same_region = stores_df[stores_df["region"] == cust_region]
    diff_region = stores_df[stores_df["region"] != cust_region]

    if same_region.empty or diff_region.empty:
        pytest.skip("Not enough stores across multiple regions")

    same_store_id = same_region.iloc[rng.randrange(len(same_region))]["store_id"]
    diff_store_id = diff_region.iloc[rng.randrange(len(diff_region))]["store_id"]

    fee_same = get_shipping_fee(ctx, same_store_id, customer_id)
    fee_diff = get_shipping_fee(ctx, diff_store_id, customer_id)

    assert (
        fee_diff > fee_same
    ), f"Cross-region fee {fee_diff:.2f} should exceed same-region fee {fee_same:.2f}"


def test_transaction_lookup_flow_get_shipping_fee_online_retail_base_fee(
    ctx, seed: int = 42
):
    """
    Integration contract: online store must have a higher
    base shipping fee than a retail store in the same area.
    """
    rng = random.Random(seed)
    customer = _build_customer_with_location(ctx)
    customer_id = customer["customer_id"]

    online_store_id = ctx.stores.online_store_id
    retail_store_id = rng.choice(ctx.stores.retail_store_ids)

    online_fee = get_shipping_fee(ctx, online_store_id, customer_id)
    retail_fee = get_shipping_fee(ctx, retail_store_id, customer_id)

    assert (
        online_fee >= 8
    ), f"Online shipping fee {online_fee:.2f} is below the minimum base of 8"
    assert (
        retail_fee >= 4
    ), f"Retail shipping fee {online_fee:.2f} is below the minimum base of 4"


# ============================================================
# opt_for_delivery()
# ============================================================
# Integration contract: uses customer + store + promotion data


def test_transaction_lookup_flow_opt_for_delivery(ctx, seed: int = 42):
    rng = random.Random(seed)
    customer_id = rng.choice(ctx.customers.customer_ids)
    store_id = rng.choice(ctx.stores.store_ids)
    df = ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
    )
    shipping_promo = shipping_promo.to_dict() if shipping_promo is not None else None
    cart_subtotal = rng.randint(10, 500)
    result = opt_for_delivery(ctx, customer_id, store_id, shipping_promo, cart_subtotal)
    assert isinstance(result, bool)
    assert result <= 85.0


def test_transaction_lookup_flow_opt_for_delivery_free_shipping_increase_opt_in_rate(
    monkeypatch, ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer_id = rng.choice(ctx.customers.customer_ids)
    store_id = rng.choice(ctx.stores.store_ids)
    df = ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
        .to_dict()
    )
    cart_subtotal = rng.randint(10, 500)

    monkeypatch.setattr(random, "random", lambda: next(itertools.cycle([0.1, 0.9])))

    N = 2000

    result_no_free_shipping = sum(
        opt_for_delivery(ctx, customer_id, store_id, None, cart_subtotal)
        for _ in range(N)
    )
    result_has_free_shipping = sum(
        opt_for_delivery(ctx, customer_id, store_id, shipping_promo, cart_subtotal)
        for _ in range(N)
    )
    assert result_no_free_shipping <= result_has_free_shipping


def test_transaction_lookup_flow_opt_for_delivery_high_cart_value_increase_opt_in_rate(
    monkeypatch, ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer_id = rng.choice(ctx.customers.customer_ids)
    store_id = rng.choice(ctx.stores.store_ids)
    df = ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
        .to_dict()
    )

    monkeypatch.setattr(random, "random", lambda: next(itertools.cycle([0.1, 0.9])))

    N = 2000

    result_low_cart_value = sum(
        opt_for_delivery(ctx, customer_id, store_id, shipping_promo, 20)
        for _ in range(N)
    )
    result_high_cart_value = sum(
        opt_for_delivery(ctx, customer_id, store_id, shipping_promo, 200)
        for _ in range(N)
    )
    assert result_low_cart_value <= result_high_cart_value


def test_transaction_lookup_flow_opt_for_delivery_cross_region_increase_opt_in_rate(
    monkeypatch, ctx, seed: int = 42
):
    customer = {"customer_id": "CUST001", "region": "Central"}
    customer_id = customer["customer_id"]
    cust_region = customer["region"]

    df = ctx.stores.stores_df
    store_1 = df[df["region"] == cust_region].sample(n=1, random_state=seed).iloc[0]
    store_2 = df[df["region"] != cust_region].sample(n=1, random_state=seed).iloc[0]

    df = ctx.promotions.promotions_df
    shipping_promo = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(n=1, random_state=seed)
        .iloc[0]
        .to_dict()
    )

    monkeypatch.setattr(random, "random", lambda: next(itertools.cycle([0.1, 0.9])))

    N = 2000

    result_same_region = (
        sum(
            opt_for_delivery(ctx, customer_id, store_1["store_id"], shipping_promo, 20)
            for _ in range(N)
        )
        / N
    )

    result_cross_region = (
        sum(
            opt_for_delivery(ctx, customer_id, store_2["store_id"], shipping_promo, 20)
            for _ in range(N)
        )
        / N
    )

    assert result_cross_region >= result_same_region


# ============================================================
# get_active_bundle_pricing()
# ============================================================
# Integration contract: uses bundle pricing data


def test_transaction_lookup_flow_get_active_bundle_pricing(ctx):
    bundle = _build_bundle(ctx)
    bundle_id = bundle["bundle_id"]
    df = ctx.bundles.bundle_pricings_df
    row = df[df["bundle_id"] == bundle_id].sample(1).iloc[0]
    transaction_date = row["effective_start_date"]

    result = get_active_bundle_pricing(ctx, bundle_id, transaction_date)
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
