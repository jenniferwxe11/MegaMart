import random
from collections import Counter

import pandas as pd
from faker import Faker

from data_generation.config.constants import DATA_END_DATE, DATA_START_DATE
from data_generation.config.customers_config import TARGET_SEGMENT

fake = Faker()
fake.seed_instance(42)


def _build_datetime():
    return fake.date_time_between(
        start_date=pd.Timestamp(DATA_START_DATE), end_date=pd.Timestamp(DATA_END_DATE)
    )


def _build_date_range():
    start = fake.date_between(
        start_date=pd.Timestamp(DATA_START_DATE), end_date=pd.Timestamp(DATA_END_DATE)
    )
    end = fake.date_between(
        start_date=pd.Timestamp(DATA_START_DATE), end_date=pd.Timestamp(DATA_END_DATE)
    )
    return start, end


def _build_datetime_range():
    start = fake.date_time_between(
        start_date=pd.Timestamp(DATA_START_DATE), end_date=pd.Timestamp(DATA_END_DATE)
    )
    end = fake.date_time_between(
        start_date=pd.Timestamp(DATA_START_DATE), end_date=pd.Timestamp(DATA_END_DATE)
    )
    return start, end


def _build_customer_segment(seed: int = 42):
    rng = random.Random(seed)

    return rng.choices(
        list(TARGET_SEGMENT.keys()),
        weights=list(TARGET_SEGMENT.values()),
        k=1,
    )[0]


def _build_customer(ctx, seed: int = 42):
    rng = random.Random(seed)
    df = ctx.customers.customers_df
    return df.iloc[rng.randrange(len(df))]


def _build_customer_with_location(ctx, seed: int = 42):
    rng = random.Random(seed)
    df = ctx.customers.customers_df

    customers_with_location = df[df["region"].notna()]

    if customers_with_location.empty:
        return None

    customers_with_location = customers_with_location.reset_index(drop=True)
    return customers_with_location.iloc[rng.randrange(len(customers_with_location))]


def _build_category(ctx, n, seed: int = 42):
    """
    Returns valid categories that has products.
    """
    rng = random.Random(seed)

    categories = [
        category
        for category, product_ids in ctx.products.category_to_products.items()
        if product_ids
    ]

    if len(categories) < n:
        raise ValueError(f"Not enough categories. Need {n}, got {len(categories)}")

    return rng.sample(categories, n)


def _build_category_product_id(ctx, category, seed: int = 42):
    rng = random.Random(seed)
    product_ids = ctx.products.category_to_products[category]
    return rng.choice(product_ids)


def _build_campaign(ctx, seed: int = 42):
    rng = random.Random(seed)
    df = ctx.campaigns.campaigns_df
    return df.iloc[rng.randrange(len(df))]


def _build_product_list(ctx, n, seed: int = 42):
    rng = random.Random(seed)
    product_ids = ctx.products.product_ids
    if len(product_ids) < n:
        raise ValueError(f"Not enough products. Need {n}, got {len(product_ids)}")

    return rng.sample(product_ids, n)


def _build_bundle_products_dict(ctx, size=2, seed: int = 42):
    rng = random.Random(seed)
    product_ids = ctx.products.product_ids
    return [(rng.choice(product_ids), rng.randint(1, 3)) for _ in range(size)]


def _build_valid_bundle_cart(ctx, bundle_id):
    required_items = ctx.bundles.bundle_dict[bundle_id]

    cart = [{"product_id": pid, "quantity": qty} for pid, qty in required_items.items()]

    return cart


def _build_insufficient_quantity_bundle_cart(ctx, bundle_id):
    required_items = ctx.bundles.bundle_dict[bundle_id]

    cart = [{"product_id": pid, "quantity": qty} for pid, qty in required_items.items()]

    # Try to create insufficient quantity
    for item in cart:
        if item["quantity"] > 1:
            item["quantity"] -= 1
            return cart

    # Fallback: all quantities are 1, simulate insufficiency by removing one item
    cart.pop()
    return cart


def _build_bundle(ctx, seed: int = 42):
    rng = random.Random(seed)
    df = ctx.bundles.bundles_df
    return df.iloc[rng.randrange(len(df))]


def _build_bundle_lifecycle(seed: int = 42):
    rng = random.Random(seed)

    launch_days = rng.randint(60, 120)
    promo_days = rng.randint(60, 120)

    launch_end = pd.Timestamp(DATA_START_DATE) + pd.Timedelta(days=launch_days)
    promo_end = launch_end + pd.Timedelta(days=promo_days)

    phases = [
        (pd.Timestamp(DATA_START_DATE), launch_end, "LAUNCH"),
        (launch_end + pd.Timedelta(days=1), promo_end, "PROMO"),
        (promo_end + pd.Timedelta(days=1), pd.Timestamp(DATA_END_DATE), "EOL"),
    ]

    return {
        "start": pd.Timestamp(DATA_START_DATE),
        "end": pd.Timestamp(DATA_END_DATE),
        "phases": phases,
    }


def _build_bundle_pricing_inputs(seed: int = 42):
    rng = random.Random(seed)

    base_price = round(rng.uniform(80, 200), 2)
    base_discount = round(base_price * rng.uniform(0.05, 0.2), 2)

    lifecycle = _build_bundle_lifecycle(seed)

    return {
        "base_price": base_price,
        "base_discount": base_discount,
        **lifecycle,
    }


def _build_bundle_promotion(ctx, seed: int = 42):
    rng = random.Random(seed)
    df = ctx.promotions.promotions_df

    bundle_promos = df[df["promotion_scope"] == "bundle"]

    if bundle_promos.empty:
        return None

    bundle_promos = bundle_promos.reset_index(drop=True)
    return bundle_promos.iloc[rng.randrange(len(bundle_promos))]


def _build_promotion(ctx, rng):
    df = ctx.promotions.promotions_df
    return df.iloc[rng.randrange(len(df))]


def _build_non_shipping_promotion(ctx, seed: int = 42):
    rng = random.Random(seed)
    df = ctx.promotions.promotions_df

    non_shipping_promos = df[df["promotion_mechanic"] != "free_shipping"]

    if non_shipping_promos.empty:
        return None

    non_shipping_promos = non_shipping_promos.reset_index(drop=True)
    return non_shipping_promos.iloc[rng.randrange(len(non_shipping_promos))]


def _build_cart_items_for_promotion(ctx, promotion, rng):
    scope = promotion["promotion_scope"]
    target = promotion["promotion_target_id"]
    product_price_map = ctx.products.product_price_map

    if scope == "product":
        price = product_price_map.get(target)
        if price is None:
            return None

        return [
            {
                "product_id": target,
                "price": price,
                "quantity": 1,
                "category": ctx.products.product_category_map.get(target),
            }
        ]

    elif scope == "category":
        min_spend = promotion.get("min_spend")
        if pd.isna(min_spend):
            min_spend = 0

        pids = ctx.products.category_to_products.get(target, [])
        if not pids:
            return None

        cart_subtotal = 0.0
        counter = Counter()

        if min_spend == 0:
            pid = rng.choice(pids)
            price = product_price_map.get(pid)
            if price is None:
                return None

            return [
                {
                    "product_id": pid,
                    "price": price,
                    "quantity": 1,
                    "category": ctx.products.product_category_map.get(pid),
                }
            ]

        else:
            # Prevent infinite loop
            i = 0
            while cart_subtotal < min_spend and i < 100:
                pid = rng.choice(pids)
                price = product_price_map.get(pid)
                if price is None:
                    i += 1
                    continue

                qty = rng.randint(1, 3)
                counter[pid] += qty
                cart_subtotal += price * qty
                i += 1

            cart_items = [
                {
                    "product_id": pid,
                    "price": product_price_map[pid],
                    "quantity": qty,
                    "category": ctx.products.product_category_map.get(pid),
                }
                for pid, qty in counter.items()
            ]

            if not cart_items:
                return None

            return cart_items

    elif scope == "bundle":
        bundle_items = ctx.bundles.bundle_dict.get(target, {})
        if not bundle_items:
            return None

        cart_items = []

        for pid, qty in bundle_items.items():
            price = product_price_map.get(pid)
            if price is None:
                return None

            cart_items.append(
                {
                    "product_id": pid,
                    "price": price,
                    "quantity": qty,
                    "category": ctx.products.product_category_map.get(pid),
                }
            )

        return cart_items

    elif scope == "cart":
        min_spend = promotion.get("min_spend")
        if pd.isna(min_spend):
            min_spend = 0

        pids = ctx.products.product_ids
        if not pids:
            return None

        cart_subtotal = 0.0
        counter = Counter()

        # Prevent infinite loop
        i = 0
        while cart_subtotal < min_spend and i < 100:
            pid = rng.choice(pids)
            price = product_price_map.get(pid)
            if price is None:
                i += 1
                continue

            qty = rng.randint(1, 3)
            counter[pid] += qty
            cart_subtotal += price * qty
            i += 1

        cart_items = [
            {
                "product_id": pid,
                "price": product_price_map[pid],
                "quantity": qty,
                "category": ctx.products.product_category_map.get(pid),
            }
            for pid, qty in counter.items()
        ]

        if not cart_items:
            return None

        return cart_items

    return None
