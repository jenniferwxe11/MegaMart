import random
import re

from data_generation.config.products_config import (
    CATEGORY_TO_STORE,
)
from data_generation.config.store_products_config import (
    BRAND_ERROR_RATE,
    CATEGORY_ERROR_RATE,
    DESCRIPTOR_MAP,
    NAME_ERROR_RATE,
    PRICE_ERROR_RATE,
)

# ---------------------------
# Helper Functions
# ---------------------------


def distort_pack_and_size(product_name):
    """
    Simulates inconsistent formatting of pack sizes and quantities in product names.
    """
    if random.random() < 0.25:
        patterns = [
            (r"(\d+)\s*-?\s*pack", lambda m: f"{m.group(1)}pk"),
            (r"(\d+)\s*-?\s*pack", lambda m: f"{m.group(1)} x"),
            (r"(\d+)\s*(g|kg|ml|l)", lambda m: f"{m.group(1)}{m.group(2)}"),
            (r"(\d+)\s*(g|kg|ml|l)", lambda m: f"{m.group(1)} {m.group(2)}"),
        ]
        for pattern, replacement in patterns:
            if re.search(pattern, product_name, flags=re.I):
                product_name = re.sub(
                    pattern, replacement, product_name, flags=re.I, count=1
                )
                return product_name
    return product_name


def distort_unit(product_name):
    """
    Simulates inconsistent unit representations in product names.
    """
    if random.random() < 0.2:
        conversions = [
            (r"1000\s*g", "1kg"),
            (r"1\s*kg", "1000g"),
            (r"1000\s*ml", "1L"),
            (r"1\s*L", "1000ml"),
        ]
        for pattern, replacement in conversions:
            if re.search(pattern, product_name, flags=re.I):
                product_name = re.sub(
                    pattern, replacement, product_name, flags=re.I, count=1
                )
                return product_name
    return product_name


def distort_case_and_typography(product_name):
    """
    Simulates inconsistent casing and formatting of product names.
    """
    if random.random() < 0.2:
        choice = random.choice(["Lower", "Upper", "Title", "Brand Drop"])
        if choice == "Lower":
            product_name = product_name.lower()
        elif choice == "Upper":
            product_name = product_name.upper()
        elif choice == "Title":
            product_name = product_name.title()
        elif choice == "Brand Drop":
            product_name = re.sub(r"^[A-Za-z&'\-]+\s+", "", product_name, count=1)
        return product_name
    return product_name


def separator_symbol_drift(product_name):
    """
    Simulates inconsistent separators in product names.
    """
    if random.random() < 0.2:
        replacements = [
            ("-", " "),
            (" ", "_"),
            (" ", "-"),
            (".", ""),
            ("'", ""),
        ]
        old, new = random.choice(replacements)
        product_name = product_name.replace(old, new, 1)
        return product_name
    return product_name


def descriptor_substitution(product_name):
    """
    Replaces product descriptors with alternative wording.
    """
    if random.random() < 0.25:
        for original, substitutes in DESCRIPTOR_MAP.items():
            if re.search(original, product_name, flags=re.I):
                product_name = re.sub(
                    original,
                    random.choice(substitutes),
                    product_name,
                    flags=re.I,
                    count=1,
                )
                return product_name
    return product_name


def inject_name_error(product_name):
    """
    Simulates inconsistent product naming.
    """
    if random.random() < NAME_ERROR_RATE:
        product_name = distort_pack_and_size(product_name)
        product_name = distort_unit(product_name)
        product_name = distort_case_and_typography(product_name)
        product_name = separator_symbol_drift(product_name)
        product_name = descriptor_substitution(product_name)
        return product_name.strip()
    return product_name


def inject_brand_error(brand):
    """
    Simulates inconsistent brand naming.
    """
    if random.random() < BRAND_ERROR_RATE:
        brand = distort_case_and_typography(brand)
        brand = separator_symbol_drift(brand)
        return brand.strip()
    return brand


def inject_category_error(category):
    """
    Simulates inconsistent category naming.
    """
    if random.random() < CATEGORY_ERROR_RATE:
        return random.choice(CATEGORY_TO_STORE[category])
    return category


def inject_price_error(price):
    """
    Simulates inconsistent pricing.
    """
    if random.random() < PRICE_ERROR_RATE:
        mismatch_factor = random.uniform(0.85, 1.15)
        return round(price * mismatch_factor, 2)
    return price
