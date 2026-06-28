import random
from collections import Counter

import pandas as pd

from data_generation.config.clickstreams_config import (
    SEGMENT_MISSION_BIAS,
)
from data_generation.config.products_config import CATEGORY_AFFINITY
from data_generation.config.store_products_config import ESSENTIAL_CATEGORIES
from data_generation.config.transactions_config import SESSION_MISSION_TARGET_RANGE

# --------------------------------
# Generate Items in Cart Functions
# --------------------------------


def sample_products(ctx, pool, count):
    """
    Samples product for a session/cart based on category affinity.

    Behaviour:
    - Users tend to browse/purchase within related categories
    - Majority of purchase are from related categories,
       with minority of purchase being from unrelated categories
    """
    product_category_map = ctx.products.product_category_map

    selected = []

    if not pool:
        return []

    # Step 1: Select seed products to establish initial shopping intent
    # (e.g. user starts browsing snacks)
    num_seeds = random.randint(1, 3)

    seed_categories = []
    for _ in range(num_seeds):
        seed_product = random.choice(pool)
        seed_cat = product_category_map.get(seed_product)
        if seed_cat:
            seed_categories.append(seed_cat)

    all_affinity_categories = set()

    # Step 2: Expand into related (affinity) categories
    # (e.g. snacks → beverages, dairy → breakfast items)
    for seed in seed_categories:
        all_affinity_categories.add(seed)
        all_affinity_categories.update(CATEGORY_AFFINITY.get(seed, []))

    # Step 3: Sample products
    for _ in range(count):
        rand = random.random()

        # 70% from affinity categories (focused shopping behaviour)
        if rand < 0.7:
            candidates = [
                pid
                for pid in pool
                if product_category_map.get(pid) in all_affinity_categories
            ]
            if not candidates:
                candidates = pool

        # 30% from full pool (exploration/impulse browsing)
        else:
            candidates = pool

        if candidates:
            selected.append(random.choice(candidates))

    return selected


def generate_cart_items(
    ctx,
    customer_segment,
    store_id,
):
    """
    Generates a realistic shopping cart for in store transactions.

    Criteria:
    - 60–70% essentials
    - Category affinity clustering (items from similar categories)
    - Allows repetition (multiple quantities of same product)
    - Applies mission driven intent bias (e.g. stock up mission → larger cart size)
    - Customer segment determines mission bias
    """
    store_product_name_map = ctx.store_catalogues.store_product_name_map
    store_product_category_map = ctx.store_catalogues.store_product_category_map
    store_product_price_map = ctx.store_catalogues.store_product_price_map
    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map
    product_price_map = ctx.products.product_price_map

    # Assign shopping mission to determine cart size
    if pd.isna(customer_segment):

        mission_choice = random.choices(
            list(SESSION_MISSION_TARGET_RANGE.keys()), weights=[0.3, 0.4, 0.2, 0.1], k=1
        )[0]
    else:
        mission_weights = SEGMENT_MISSION_BIAS.get(customer_segment, {})
        missions = list(SESSION_MISSION_TARGET_RANGE.keys())
        mission_choice = random.choices(
            missions, weights=[mission_weights.get(m, 0.0) for m in missions], k=1
        )[0]

    low, high = SESSION_MISSION_TARGET_RANGE[mission_choice]
    num_products = random.randint(low, high)

    cart_items = []

    # Split essentials vs non-essentials
    essential_ratio = random.uniform(0.6, 0.7)
    num_essentials = int(num_products * essential_ratio)
    num_non_essentials = num_products - num_essentials

    essential_products = [
        pid
        for pid in product_ids
        if product_category_map.get(pid) in ESSENTIAL_CATEGORIES
    ]

    non_essential_products = [
        pid
        for pid in product_ids
        if product_category_map.get(pid) not in ESSENTIAL_CATEGORIES
    ]

    # Build cart
    selected_products = []
    selected_products += sample_products(ctx, essential_products, num_essentials)
    selected_products += sample_products(
        ctx, non_essential_products, num_non_essentials
    )

    # Input cart item details
    cart_counts = Counter(selected_products)
    for product_id, quantity in cart_counts.items():
        name = store_product_name_map.get(
            (store_id, product_id)
        ) or product_name_map.get(product_id)
        category = store_product_category_map.get(
            (store_id, product_id)
        ) or product_category_map.get(product_id)
        price = store_product_price_map.get(
            (store_id, product_id)
        ) or product_price_map.get(product_id)

        if price is None:
            continue

        cart_items.append(
            {
                "product_id": product_id,
                "name": name,
                "price": price,
                "category": category,
                "quantity": quantity,
            }
        )

    return cart_items
