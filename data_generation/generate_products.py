import random
from datetime import timedelta, date

import pandas as pd
from config import (
    BRANDS,
    CATEGORIES,
    CATEGORY_COST_MARGIN,
    CATEGORY_ITEMS,
    CATEGORY_PRICE_RANGES,
    NUM_PRODUCTS,
)
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

products = []
product_ids = []

for i in range(1, NUM_PRODUCTS + 1):
    pid = f"PROD{i:03d}"
    product_ids.append(pid)

    category = random.choice(CATEGORIES)
    brand = random.choice(BRANDS.get(category, ["Generic"]))
    item = random.choice(CATEGORY_ITEMS.get(category, ["Item"]))

    product_name = f"{random.choice(['Premium', 'Classic', 'Deluxe', 'Extra'])} {brand} {item}"

    # Prices
    min_price, max_price = CATEGORY_PRICE_RANGES.get(category, (1.5, 100))
    selling_price = round(random.uniform(min_price, max_price), 2)
    min_margin, max_margin = CATEGORY_COST_MARGIN.get(category, (0.5, 0.95))
    cost_price = round(selling_price * random.uniform(min_margin, max_margin), 2)

    status = random.choices(
        ["Active", "Discontinued"], weights=[0.95, 0.05]
    )[0]

    promotion_type = random.choices(
        [None, "Buy One Get One", "Discounted"], weights=[0.85, 0.05, 0.10]
    )[0]

    promotion_start_date = None
    promotion_end_date = None
    discount_percentage = None
    bogo_flag = False

    if promotion_type == "Discounted":
        discount_percentage = random.randint(5, 20)
    elif promotion_type == "Buy One Get One":
        bogo_flag = True

    if promotion_type:
        promotion_start_date = fake.date_between(start_date=date(2024,1,1), end_date=date(2024,12,31))
        promotion_end_date = promotion_start_date + timedelta(days=random.randint(3, 14))  # 3-14 days promotion

    discontinuation_date = None

    if status == "Discontinued":
        if promotion_end_date:
            discontinuation_date = fake.date_between(start_date=promotion_end_date, end_date=date(2024,12,31))
        else:
            discontinuation_date = fake.date_between(start_date=date(2024,1,1), end_date=date(2024,12,31))

    stock_quantity = random.randint(0,300)

    products.append(
        {
            "product_id": pid,
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "selling_price": selling_price,
            "cost_price": cost_price,
            "status": status,
            "promotion_type": promotion_type,
            "bogo_flag": bogo_flag,
            "discount_percentage": discount_percentage,
            "promotion_start_date": promotion_start_date,
            "promotion_end_date": promotion_end_date,
            "discontinuation_date": discontinuation_date,
            "stock_quantity": stock_quantity,
        }
    )

df = pd.DataFrame(products)
df.to_csv("data_generation/raw_data/products_raw.csv", index=False)
print("products_raw.csv file generated")
