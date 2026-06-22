import random

import pandas as pd
from faker import Faker

from data_generation.config.constants import DATA_END_DATE, DATA_START_DATE
from data_generation.config.customers_config import TARGET_SEGMENT
from data_generation.config.promotions_config import (
    MECHANIC_SCOPE_RULES,
    PROMOTION_TYPE_PROB,
)
from data_generation.services.promotions.promotion_service import (
    generate_promotion_value,
)

fake = Faker()


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


def _build_product(ctx, category, seed: int = 42):
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
    product_ids = list(ctx.products.product_price_map.keys())
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

    lifecycle = _build_bundle_lifecycle()

    return {
        "base_price": base_price,
        "base_discount": base_discount,
        **lifecycle,
    }


def _build_promotion(ctx, seed: int = 42):
    rng = random.Random(seed)
    df = ctx.promotions.promotions_df
    return df.iloc[rng.randrange(len(df))]


def _build_promotion_variables(ctx, seed: int = 42):
    rng = random.Random(seed)
    promotion_mechanic = rng.choices(
        list(PROMOTION_TYPE_PROB.keys()),
        weights=list(PROMOTION_TYPE_PROB.values()),
        k=1,
    )[0]
    promotion_scope = MECHANIC_SCOPE_RULES[promotion_mechanic]
    promotion_target_id = ""
    category = ""
    if promotion_scope == "category":
        category = _build_category(ctx, 1)[0]
        promotion_target_id = category
    elif promotion_scope == "product":
        category = _build_category(ctx, 1)[0]
        promotion_target_id = _build_product(ctx, category)
    elif promotion_scope == "bundle":
        bundle = _build_bundle(ctx)
        promotion_target_id = bundle["bundle_id"]
        category = bundle["category"]

    return promotion_mechanic, promotion_scope, promotion_target_id, category


def _build_promotion_value(
    ctx, promotion_mechanic, promotion_scope, promotion_target_id, category
):
    return generate_promotion_value(
        ctx,
        promotion_mechanic,
        promotion_scope,
        promotion_target_id,
        category,
    )
