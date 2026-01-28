import random
import re

import pandas as pd
from config import (
    BRANDS,
    CATEGORIES,
    CATEGORY_COST_MARGIN,
    CATEGORY_ITEMS,
    CATEGORY_PRICE_RANGES,
    CATEGORY_PROFILES,
    NUM_PRODUCTS,
    SUBCATEGORIES,
    SUBCATEGORY_ITEMS,
)

random.seed(42)

products = []
product_ids = []


def parse_net_content(net_content):
    if net_content is None:
        return None
    if net_content == "Loose":
        return 1
    net_content = net_content.lower().strip()
    if net_content.endswith("kg"):
        return float(net_content.replace("kg", "")) * 1000
    elif net_content.endswith("g"):
        return float(net_content.replace("g", ""))
    elif net_content.endswith("ml"):
        return float(net_content.replace("ml", ""))
    elif net_content.endswith("l"):
        return float(net_content.replace("l", "")) * 1000
    return None


def parse_pack_quantity(pack_quantity):
    if pack_quantity is None:
        return 1
    m = re.match(r"(\d+)-pack", pack_quantity)
    return int(m.group(1)) if m else 1


def pack_discount(pack_quantity):
    if pack_quantity is None:
        return 1.0
    m = re.match(r"(\d+)-pack", pack_quantity)
    qty = int(m.group(1)) if m else 1
    discount = 0.05 * (qty - 1)
    factor = max(0.6, 1 - discount)
    return factor


def generate_price(base_price_per_unit, net_content, pack_quantity):
    net_value = parse_net_content(net_content)
    units = parse_pack_quantity(pack_quantity)

    # size multiplier
    if net_value is None:
        net_multiplier = 1
    else:
        net_multiplier = net_value / 100

    # larger pack -> cheaper per unit
    discount_factor = pack_discount(pack_quantity)
    price = base_price_per_unit * net_multiplier * units * discount_factor

    # floor price protection
    price = max(price, base_price_per_unit * units * 0.4)
    return round(price, 2)


for i in range(1, NUM_PRODUCTS + 1):
    product_id = f"PROD{i:03d}"
    product_ids.append(product_id)

    # pick a category
    category = random.choice(CATEGORIES)
    subcategory = None

    # check if category has subcategories
    if category in SUBCATEGORIES:
        subcategory = random.choice(SUBCATEGORIES[category])
        brand = random.choice(BRANDS[subcategory])
        item = random.choice(SUBCATEGORY_ITEMS[subcategory])
    else:
        brand = random.choice(BRANDS[category])
        item = random.choice(CATEGORY_ITEMS[category])

    # category level profiles
    profile = CATEGORY_PROFILES[category]
    variant = random.choice(profile.get("variants", [None]))
    net_content = random.choice(profile.get("net_content", [None]))
    pack_quantity = random.choice(profile.get("pack_quantity", [None]))
    colour = random.choice(profile.get("colour", [None]))

    # build product name
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

    # Prices
    min_price, max_price = CATEGORY_PRICE_RANGES.get(category, (1.5, 10))
    selling_price = round(random.uniform(min_price, max_price), 2)
    selling_price = generate_price(selling_price, net_content, pack_quantity)
    min_margin, max_margin = CATEGORY_COST_MARGIN.get(category, (0.5, 0.95))
    cost_price = round(selling_price * random.uniform(min_margin, max_margin), 2)

    products.append(
        {
            "product_id": product_id,
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "selling_price": selling_price,
            "cost_price": cost_price,
        }
    )

df = pd.DataFrame(products)
df.to_csv("data_generation/raw_data/products_raw.csv", index=False)
print("products_raw.csv file generated")
