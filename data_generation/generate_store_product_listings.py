import random
import re
import pandas as pd
from config import (
    BRAND_ERROR_RATE,
    CATEGORY_TO_STORE,
    CATEGORY_ERROR_RATE,
    DESCRIPTOR_MAP,
    NAME_ERROR_RATE,
    PRICE_ERROR_RATE,
    STORE_TYPE_CONFIG,
    ESSENTIAL_CATEGORIES,
)

random.seed(42)

stores_df = pd.read_csv("data_generation/raw_data/stores_raw.csv")
store_ids = stores_df["store_id"].dropna().tolist()

products_df = pd.read_csv("data_generation/raw_data/products_raw.csv")
product_ids = products_df["product_id"].dropna().tolist()

essential_product_ids = products_df[products_df["category"].isin(ESSENTIAL_CATEGORIES)]["product_id"].tolist()
non_essentials_product_ids = list(set(product_ids) - set(essential_product_ids))

def distort_pack_and_size(product_name):
    if random.random() < 0.25:
        patterns = [
            (r"(\d+)\s*-?\s*pack", lambda m: f"{m.group(1)}pk"),
            (r"(\d+)\s*-?\s*pack", lambda m: f"{m.group(1)} x"),
            (r"(\d+)\s*(g|kg|ml|l)", lambda m: f"{m.group(1)}{m.group(2)}"),
            (r"(\d+)\s*(g|kg|ml|l)", lambda m: f"{m.group(1)} {m.group(2)}"),
        ]
        for pattern, replacement in patterns:
            if re.search(pattern, product_name, flags=re.I):
                product_name = re.sub(pattern, replacement, product_name, flags=re.I, count=1)
                return product_name
    return product_name

def unit_normalisation(product_name):
    if random.random() < 0.2:
        conversions = [
            (r"1000\s*g", "1kg"),
            (r"1\s*kg", "1000g"),
            (r"1000\s*ml", "1L"),
            (r"1\s*L", "1000ml"),
        ]
        for pattern, replacement in conversions:
            if re.search(pattern, product_name, flags=re.I):
                product_name = re.sub(pattern, replacement, product_name, flags=re.I, count=1)
                return product_name
    return product_name

def case_and_typography(product_name):
    if random.random() < 0.2:
        choice = random.choice(["lower", "upper", "title", "brand_drop"])
        if choice == "lower":
            product_name = product_name.lower()
        elif choice == "upper":
            product_name = product_name.upper()
        elif choice == "title":
            product_name = product_name.title()
        elif choice == "brand_drop":
            product_name = re.sub(r"^[A-Za-z&'\-]+\s+", "", product_name, count=1)
        return product_name
    return product_name

def separator_symbol_drift(product_name):
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
    if random.random() < 0.25:
        for original, substitutes in DESCRIPTOR_MAP.items():
            if re.search(original, product_name, flags=re.I):
                product_name = re.sub(original, random.choice(substitutes), product_name, flags=re.I, count=1)
                return product_name
    return product_name

def inject_name_error(product_name):
    if random.random() < NAME_ERROR_RATE:
        product_name = distort_pack_and_size(product_name)
        product_name = unit_normalisation(product_name)
        product_name = case_and_typography(product_name)
        product_name = separator_symbol_drift(product_name)
        product_name = descriptor_substitution(product_name)
        return product_name.strip()
    return product_name

def inject_brand_error(brand):
    if random.random() < BRAND_ERROR_RATE:
        brand = case_and_typography(brand)
        brand = separator_symbol_drift(brand)
        return brand.strip()
    return brand

def inject_category_error(category):
    if random.random() < CATEGORY_ERROR_RATE:
        return random.choice(CATEGORY_TO_STORE[category])
    return category

def inject_price_error(price):
    if random.random() < PRICE_ERROR_RATE:
        mismatch_factor = random.uniform(0.85, 1.15)
        return round(price * mismatch_factor, 2)
    return price

store_product_listings = []
for store_id in store_ids:
    if store_id == "STOR002":
        break
    store_type = stores_df.loc[stores_df["store_id"] == store_id, "store_type"].iloc[0]

    # determine how much product the store carries
    assort_low, assort_high = STORE_TYPE_CONFIG[store_type]["Assortment"]
    total_products = int(len(product_ids) * random.uniform(assort_low, assort_high))

    # ensure essential items are always present
    essen_low, essen_high = STORE_TYPE_CONFIG[store_type]["Essential"]
    essential_count = min(int(total_products * random.uniform(essen_low, essen_high)), len(essential_product_ids))
    selected_essentials = random.sample(essential_product_ids, essential_count)

    # fill up the rest of the assortment
    remaining_slots = max(total_products - essential_count, 0)
    selected_non_essentials = random.sample(
        non_essentials_product_ids,
        min(remaining_slots, len(non_essentials_product_ids))
    )
    selected_product = selected_essentials + selected_non_essentials

    for product_id in selected_product:
        product_row = products_df[products_df["product_id"] == product_id]

        # get original details
        product_name = product_row["product_name"].iloc[0]
        brand = product_row["brand"].iloc[0]
        category = product_row["category"].iloc[0]
        selling_price = product_row["selling_price"].iloc[0]

        # inject errors
        store_product_name = inject_name_error(product_name)
        store_brand = inject_brand_error(brand)
        store_category = inject_category_error(category)
        store_selling_price = inject_price_error(selling_price)

        store_product_listings.append(
            {
                "store_id": store_id,
                "product_id": product_id,
                "store_product_name": store_product_name,
                "store_brand": store_brand,
                "store_category": store_category,
                "store_selling_price": store_selling_price,
            }
        )

df_store_product_listings = pd.DataFrame(store_product_listings)
df_store_product_listings.to_csv("data_generation/raw_data/store_product_listings_raw.csv", index=False)
print("store_product_listings_raw.csv file generated")
