import random
from typing import Any

import pandas as pd

from data_generation.config.generation_config import NUM_PRODUCTS
from data_generation.config.products_config import (
    BRANDS,
    CATEGORY_ITEMS,
    CATEGORY_PRODUCT_DISTRIBUTION,
    CATEGORY_PROFILES,
    SUBCATEGORIES,
    SUBCATEGORY_ITEMS,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.products.product_attribute_service import (
    generate_price,
    get_price_range,
)
from data_generation.utils.io_utils import save


@register("products_generator")
def products_generator(ctx: GenerationContext):
    # ---------------------------
    # Storage
    # ---------------------------

    products: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    i = 1
    while len(products) < NUM_PRODUCTS:
        product_id = f"PROD{i:03d}"

        # Simulate realistic category mix based on supply distributions
        category = random.choices(
            list(CATEGORY_PRODUCT_DISTRIBUTION.keys()),
            weights=list(CATEGORY_PRODUCT_DISTRIBUTION.values()),
            k=1,
        )[0]

        # Ensure product hierarchy consistency (subcategory/brand/item)
        subcategory = None
        if category in SUBCATEGORIES:
            subcategory = random.choice(SUBCATEGORIES[category])
            brand = random.choice(BRANDS[subcategory])
            item = random.choice(SUBCATEGORY_ITEMS[subcategory])
        else:
            brand = random.choice(BRANDS[category])
            item = random.choice(CATEGORY_ITEMS[category])

        # Apply category specific product attributes
        profile = CATEGORY_PROFILES[category]
        variant = random.choice(profile.get("variants", [None]))
        net_content = random.choice(profile.get("net_content", [None]))
        pack_quantity = random.choice(profile.get("pack_quantity", [None]))
        colour = random.choice(profile.get("colour", [None]))

        # Construct product name using retail product naming conventions
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

        # Generate product pricing
        min_price, max_price = get_price_range(category, subcategory, item)
        selling_unit_price = round(random.uniform(min_price, max_price), 2)
        selling_price, cost_price = generate_price(
            category, selling_unit_price, net_content, pack_quantity
        )

        # Store Product Record
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

        i += 1

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(products), "products_raw.csv")
