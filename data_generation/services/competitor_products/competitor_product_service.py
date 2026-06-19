import random

import pandas as pd
from faker import Faker

from data_generation.config.competitor_products_config import (
    CATEGORY_TO_COMPETITOR,
    COMPETITOR_BRANDS,
    COMPETITOR_CATEGORIES,
    COMPETITOR_CATEGORY_ITEMS,
    COMPETITOR_CATEGORY_PRICE_RANGES,
    COMPETITOR_EXCLUSIVE_BRAND_BIAS,
    COMPETITOR_EXCLUSIVE_BRANDS,
    NAME_PATTERNS,
    TERM_SWAPS,
)
from data_generation.config.constants import DATA_END_DATE, DATA_START_DATE
from data_generation.config.products_config import (
    BRANDS,
    CATEGORIES,
    CATEGORY_ITEMS,
    CATEGORY_PRICE_RANGES,
    CATEGORY_PROFILES,
)

fake = Faker()
# ---------------------------
# Helper Functions
# ---------------------------


def get_category_reference(category):
    """
    Resolves a competitor category into a usable reference set.

    Purpose:
    - Ensure downstream generation never fails due to missing category mappings.
    """
    # Case 1: Competitor specific category exists
    if category in COMPETITOR_CATEGORY_ITEMS:
        items = COMPETITOR_CATEGORY_ITEMS.get(category, [])
        brands = COMPETITOR_BRANDS.get(category, [])
        selling_price_range = COMPETITOR_CATEGORY_PRICE_RANGES.get(category, ())

        # Fallback if incomplete competitor data
        if not brands or not items:
            base_category = None
            for (
                megamart_category,
                competitor_categories,
            ) in CATEGORY_TO_COMPETITOR.items():
                if category in competitor_categories:
                    base_category = megamart_category
                    break

            if not base_category:
                base_category = random.choice(CATEGORIES)

            items = items or CATEGORY_ITEMS.get(base_category, [])
            brands = brands or BRANDS.get(base_category, [])
            selling_price_range = selling_price_range or CATEGORY_PRICE_RANGES.get(
                base_category, ()
            )

        return category, items, brands, selling_price_range

    # Case 2: Map to Megamart base category
    base_category = None
    for megamart_category, competitor_categories in CATEGORY_TO_COMPETITOR.items():
        if category in competitor_categories:
            base_category = megamart_category
            break

    # Final fallback
    if not base_category:
        base_category = random.choice(CATEGORIES)

    items = CATEGORY_ITEMS.get(base_category, [])
    brands = BRANDS.get(base_category, [])
    selling_price_range = CATEGORY_PRICE_RANGES.get(base_category, ())

    return base_category, items, brands, selling_price_range


def generate_scraped_category(category, category_noise):
    """
    Simulates inconsistencies in competitor category labelling.

    Purpose:
    - Reflect real-world scraping challenges where category taxonomies are inconsistent across retailers.
    """
    scraped_category = category
    if random.random() < category_noise:
        scraped_category = random.choice(
            CATEGORY_TO_COMPETITOR.get(category, [category])
        )

    return scraped_category


def generate_product_name(base_category, brand, item):
    """
    Generates a synthetic product name by combining brand, item, and optional
    category specific attributes (variant, colour, net content, pack quantity).
    """
    profile = CATEGORY_PROFILES.get(
        base_category,
        {
            "variants": [None],
            "net_content": [None],
            "pack_quantity": [None],
            "colour": [None],
        },
    )
    variant = random.choice(profile.get("variants", [None]))
    net_content = random.choice(profile.get("net_content", [None]))
    pack_quantity = random.choice(profile.get("pack_quantity", [None]))
    colour = random.choice(profile.get("colour", [None]))

    # Build product name
    product_name_parts = [brand]
    if variant:
        product_name_parts.append(variant)
    product_name_parts.append(item)
    if colour:
        product_name_parts.append(colour)
    if net_content:
        product_name_parts.append(net_content)
    if pack_quantity:
        product_name_parts.append(pack_quantity)

    product_name = " ".join(product_name_parts)

    return product_name


def generate_scraped_name(brand, product_name, name_noise):
    """
    Generates realistic "messy" product names from competitor sources.

    Transformation applied:
    - Random removal of words
    - Word order shuffling
    - Term substitution (synonyms)
    - Random casing variations
    - Flexible formatting patterns

    Purpose:
    - Mimic real world scraped data variability to stress test product matching and normalization pipelines.
    """
    # Split product name into words
    tokens = product_name.split()

    # Randomly drop words to simulate messy names
    tokens = [t for t in tokens if random.random() >= name_noise]

    # Ensure at least some words remain
    if not tokens:
        tokens = product_name.split()

    # Optionally shuffle word order
    if random.random() >= name_noise:
        random.shuffle(tokens)

    # Remove duplicate brand mention
    tokens = [t for t in tokens if t != brand]

    # Apply term substitution with synonyms
    for i, token in enumerate(tokens):
        if token in TERM_SWAPS and random.random() >= name_noise:
            tokens[i] = random.choice(TERM_SWAPS[token])

    product_field = " ".join(tokens)

    # Random casing
    if random.random() >= name_noise:
        brand = brand.upper()
    if random.random() >= name_noise:
        product_field = product_field.upper()

    name_components = {
        "brand": brand,
        "product": product_field,
    }

    # Pick a random formatting pattern
    pattern = random.choice(list(NAME_PATTERNS))
    return pattern.format(**name_components).replace("None", "").strip()


def generate_scraped_price(selling_price, price_bias):
    """
    Simulates competitor pricing deviations from Megamart baseline.

    Components:
    - Strategic bias (premium vs discount positioning)
    - Random noise (day to day fluctuation)
    - Absolute variation (higher volatility for higher price items)

    Safeguard:
    - Enforces minimum price floor (50% of base price)

    Purpose:
    - Reflect realistic competitor pricing behaviour.
    """
    min_bias, max_bias = price_bias

    # Bias
    bias = random.uniform(min_bias, max_bias)

    # Random noise
    noise = random.uniform(-0.05, 0.05)

    # Absolute variation
    if selling_price < 2:
        abs_noise = random.uniform(-0.3, 0.5)
    elif selling_price < 10:
        abs_noise = random.uniform(-1.0, 1.5)
    elif selling_price < 50:
        abs_noise = random.uniform(-3, 5)
    else:
        abs_noise = random.uniform(-10, 20)

    scraped_price = selling_price * (1 + bias + noise) + abs_noise

    # Price floor safeguard
    scraped_price = max(scraped_price, selling_price * 0.5)

    return round(scraped_price, 2)


def get_competitor_products(ctx, competitor, configuration):
    """
    Constructs a full competitor product catalogue.

    Structure:
    1. Shared Products (overlap with Megamart)
        - Represents comparable SKUs across retailers

    2. Exclusive Products
        - Unique assortment differentiation
        - Includes competitor specific brands and items

    Purpose:
    - Simulate realistic assortment overlap + differentiation across competitors.
    """
    products_df = ctx.products.products_df

    competitor_products = []
    seen_competitor_name_keys = set()  # (competitor, scraped_product_name)
    seen_competitor_id_keys = set()  # (competitor, product_id)

    # --- Shared Products ---
    shared_products = products_df.sample(
        frac=random.uniform(0.4, 0.8), replace=False
    ).drop_duplicates(subset=["product_id"])

    for _, product in shared_products.iterrows():
        product_id = product["product_id"]

        scraped_product_name = generate_scraped_name(
            product["brand"], product["product_name"], configuration["name_noise"]
        )

        # Deduplicate for same product id
        id_key = (competitor, product_id)
        if id_key in seen_competitor_id_keys:
            continue
        seen_competitor_id_keys.add(id_key)

        # Deduplicate for same product name
        name_key = (competitor, scraped_product_name)
        if name_key in seen_competitor_name_keys:
            continue
        seen_competitor_name_keys.add(name_key)

        scraped_category = generate_scraped_category(
            product["category"], configuration["category_noise"]
        )

        scraped_price = generate_scraped_price(
            product["selling_price"], price_bias=configuration["price_bias"]
        )

        # Prevent NULL
        if scraped_product_name is None or competitor is None or scraped_price is None:
            continue

        competitor_products.append(
            {
                "product_id": product_id,
                "base_product_name": product["product_name"],
                "scraped_product_name": scraped_product_name,
                "brand": product["brand"],
                "category": scraped_category,
                "selling_price": scraped_price,
                "is_exclusive": False,
            }
        )

    # --- Exclusive Products ---
    exclusive_product_count = int(len(shared_products) * random.uniform(0.15, 0.35))
    for _ in range(exclusive_product_count):

        category_pool = COMPETITOR_CATEGORIES.get(competitor, [])
        if not category_pool:
            continue

        category = random.choice(category_pool)

        # Get reference for items and brands
        base_category, item_pool, brand_pool, selling_price_range = (
            get_category_reference(category)
        )

        if not item_pool or not brand_pool:
            continue

        # Pick a brand from category
        if random.random() < COMPETITOR_EXCLUSIVE_BRAND_BIAS.get(competitor, 0.1):
            brand = random.choice(COMPETITOR_EXCLUSIVE_BRANDS.get(competitor, []))
        else:
            competitor_brand_pool = COMPETITOR_BRANDS.get(category, [])
            if competitor_brand_pool:
                brand = random.choice(competitor_brand_pool)
            else:
                brand = random.choice(brand_pool)

        # Pick an item
        competitor_item_pool = COMPETITOR_CATEGORY_ITEMS.get(category, [])
        if competitor_item_pool:
            item = random.choice(competitor_item_pool)
        else:
            item = random.choice(item_pool)

        # Generate product name
        base_product_name = generate_product_name(base_category, brand, item)
        scraped_product_name = generate_scraped_name(
            brand, base_product_name, configuration["name_noise"]
        )

        # Deduplicate for same product name
        name_key = (competitor, scraped_product_name)
        if name_key in seen_competitor_name_keys:
            continue
        seen_competitor_name_keys.add(name_key)

        # Generate selling price
        competitor_selling_price_range = COMPETITOR_CATEGORY_PRICE_RANGES.get(
            category, ()
        )
        if competitor_selling_price_range:
            min_selling_price, max_selling_price = competitor_selling_price_range
        else:
            min_selling_price, max_selling_price = selling_price_range
        selling_price = round(random.uniform(min_selling_price, max_selling_price), 2)

        # Prevent NULL
        if scraped_product_name is None or competitor is None or selling_price is None:
            continue

        competitor_products.append(
            {
                "product_id": None,
                "base_product_name": base_product_name,
                "scraped_product_name": scraped_product_name,
                "brand": brand,
                "category": category,
                "selling_price": selling_price,
                "is_exclusive": True,
            }
        )

    return competitor_products


def get_scrape_batches(ctx):
    """
    Generates timestamp representing competitor data scraping events.

    Behaviour:
    - Random number of scrape batches
    - Evenly distributed across data time window (simulate staggered scraping jobs)

    Purpose:
    - Simulate periodic competitor monitoring process
    """

    scrape_batch_dates = []
    batch_count = random.randint(15, 30)

    for _ in range(batch_count):
        scrape_date = fake.date_time_between(
            start_date=pd.Timestamp(DATA_START_DATE),
            end_date=pd.Timestamp(DATA_END_DATE),
        )
        scrape_batch_dates.append(scrape_date)

    return sorted(scrape_batch_dates)
