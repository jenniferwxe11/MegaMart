import random
from datetime import timedelta

import pandas as pd
from config import (
    DATA_END_DATE,
    DATA_START_DATE,
    PRODUCT_LIFECYCLE,
    SIMULATION_DATE,
)

random.seed(42)

products_df = pd.read_csv("data_generation/raw_data/products_raw.csv")
product_ids = products_df["product_id"].dropna().tolist()

product_lifecycles = []

for product_id in product_ids:
    launch_date = DATA_START_DATE + (DATA_END_DATE - DATA_START_DATE) * (
        random.random() ** 2
    )

    if launch_date >= SIMULATION_DATE - timedelta(days=30):
        status = "New"
    else:
        status = random.choices(
            list(PRODUCT_LIFECYCLE.keys()),
            weights=list(PRODUCT_LIFECYCLE.values()),
            k=1,
        )[0]

    discontinuation_date = None
    if status == "Discontinued":
        discontinuation_date = launch_date + timedelta(days=random.randint(90, 365))

    product_lifecycles.append(
        {
            "product_id": product_id,
            "status": status,
            "launch_date": launch_date,
            "discontinuation_date": discontinuation_date,
        }
    )

df_product_lifecycles = pd.DataFrame(product_lifecycles)
df_product_lifecycles.to_csv(
    "data_generation/raw_data/product_lifecycles_raw.csv", index=False
)
print("product_lifecycles_raw.csv file generated")
