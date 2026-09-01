import random
import re

from data_generation.config.store_products_config import (
    CATEGORY_TO_STORE,
    DESCRIPTOR_MAP,
)

# ---------------------------
# Helper Functions
# ---------------------------


def distort_pack_and_size(product_name):
    """
    Simulates inconsistent formatting of pack sizes and quantities in product names.
    """

    patterns = [
        (r"(\d+)\s*-?\s*pack", lambda m: f"{m.group(1)}pk"),
        (r"(\d+)\s*-?\s*pack", lambda m: f"{m.group(1)} x"),
        (r"(\d+)\s*(g|kg|ml|l)", lambda m: f"{m.group(1)}{m.group(2)}"),
        (r"(\d+)\s*(g|kg|ml|l)", lambda m: f"{m.group(1)} {m.group(2)}"),
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, product_name, flags=re.I):
            return re.sub(
                pattern,
                replacement,
                product_name,
                flags=re.I,
                count=1,
            )

    return product_name


def distort_unit(product_name):
    """
    Simulates inconsistent unit representations in product names.
    """

    conversions = [
        (r"1000\s*g", "1kg"),
        (r"1\s*kg", "1000g"),
        (r"1000\s*ml", "1L"),
        (r"1\s*L", "1000ml"),
    ]
    for pattern, replacement in conversions:
        if re.search(pattern, product_name, flags=re.I):
            return re.sub(pattern, replacement, product_name, flags=re.I, count=1)

    return product_name


def distort_case_and_typography(word):
    """
    Simulates inconsistent casing of product names and brands.
    """

    choice = random.choice(
        [
            lambda x: x.lower(),
            lambda x: x.upper(),
            lambda x: x.title(),
        ]
    )

    return choice(word)


def separator_symbol_drift(product_name):
    """
    Simulates inconsistent separators in product names.
    """

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


def descriptor_substitution(product_name):
    """
    Replaces product descriptors with alternative wording.
    """

    for original, substitutes in DESCRIPTOR_MAP.items():
        if re.search(original, product_name, flags=re.I):
            return re.sub(
                original,
                random.choice(substitutes),
                product_name,
                flags=re.I,
                count=1,
            )

    return product_name


def inject_name_variation(product_name):
    """
    Simulates inconsistent product naming.
    """

    choice = random.choice(
        [
            lambda x: distort_pack_and_size(x),
            lambda x: distort_unit(x),
            lambda x: distort_case_and_typography(x),
            lambda x: separator_symbol_drift(x),
            lambda x: descriptor_substitution(x),
        ]
    )

    return choice(product_name).strip()


def inject_brand_variation(brand):
    """
    Simulates inconsistent brand naming.
    """

    choice = random.choice(
        [
            lambda x: distort_case_and_typography(x),
            lambda x: separator_symbol_drift(x),
        ]
    )
    return choice(brand).strip()


def inject_category_variation(category):
    """
    Simulates inconsistent category naming.
    """

    return random.choice(CATEGORY_TO_STORE[category])


def inject_price_variation(price):
    """
    Simulates inconsistent pricing.
    """

    mismatch_factor = random.uniform(0.85, 1.15)
    return round(price * mismatch_factor, 2)
