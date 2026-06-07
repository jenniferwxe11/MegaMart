import random
import re
from data_generation.config.products_config import (
    CATEGORY_COST_MARGIN,
    CATEGORY_MIN_PRICE,
    CATEGORY_PRICE_RANGES,
    PACK_PRICE_CAP,
    SUBCATEGORY_PRICE_RANGES,
    ITEM_PRICE_RANGES,
)

# ---------------------------
# Helper Functions
# ---------------------------

def parse_net_content(net_content):
    """
    Converts product size into a standard unit.
    """
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
    """
    Extracts number of units in a pack.
    """
    if pack_quantity is None:
        return 1
    m = re.match(r"(\d+)-pack", pack_quantity)
    return int(m.group(1)) if m else 1


def pack_discount(pack_quantity):
    """
    Applies bulk discount with diminishing scaling.
    """
    if pack_quantity is None:
        return 1.0
    
    m = re.match(r"(\d+)-pack", pack_quantity)
    qty = int(m.group(1)) if m else 1

    if qty <= 2:
        return random.uniform(0.9, 1.0)
    elif qty <= 6:
        return random.uniform(0.75, 0.9)
    elif qty <= 12:
        return random.uniform(0.6, 0.8)
    else:
        return random.uniform(0.5, 0.7)


def get_price_range(
        category, 
        subcategory=None, 
        item=None
):
    """
    Retrieves appropriate pricing ranges.

    Pricing hierarchy:
    Item > Subcategory > Category

    Ensures more granular products have more accurate pricing.
    """
    if item and item in ITEM_PRICE_RANGES:
        return ITEM_PRICE_RANGES[item]
    if subcategory and subcategory in SUBCATEGORY_PRICE_RANGES:
        return SUBCATEGORY_PRICE_RANGES[subcategory]
    return CATEGORY_PRICE_RANGES[category]

def generate_price(
        category,
        base_price_per_unit,
        net_content, 
        pack_quantity
):
    """
    Calculates final selling and cost price of product.

    Pricing reflects:
    - Product size and pack quantity
    - Bulk discounts
    - Margin protection
    - Minimum price constraints

    Ensures all generated prices are commercially realistic.
    """
    net_value = parse_net_content(net_content)
    units = parse_pack_quantity(pack_quantity)

    # Size multiplier
    if net_value is None:
        net_multiplier = 1
    else:
        net_multiplier = net_value / 100

    # Bulk discounts
    discount_factor = pack_discount(pack_quantity)
    price = base_price_per_unit * net_multiplier * units * discount_factor

    # Unit sanity floor
    price = max(price, base_price_per_unit * units * 0.4)

    # Minimum price constraint
    price = max(price, CATEGORY_MIN_PRICE.get(category, 0))

    # Price cap
    if category in PACK_PRICE_CAP and units > 1:
        min_per_unit, max_per_unit = PACK_PRICE_CAP[category]
        unit_price = price / units
        if unit_price > max_per_unit:
            unit_price = max_per_unit * random.uniform(0.85, 1.0)
        elif unit_price < min_per_unit:
            unit_price = min_per_unit * random.uniform(1.0, 1.15)
        price = unit_price * units

    price = min(price, base_price_per_unit * net_multiplier * units * 0.85 + 5)

    # Margin protection
    min_margin, max_margin = CATEGORY_COST_MARGIN.get(category, (0.5, 0.95))
    cost_price = price * random.uniform(min_margin, max_margin)

    # Cost cap
    cost_price = min(cost_price, price * 0.95)

    return round(price, 2), round(cost_price,2)
