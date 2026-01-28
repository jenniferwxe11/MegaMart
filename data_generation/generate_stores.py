import random

import pandas as pd
from config import MALL_TO_AREA, NUM_PHYSICAL_STORES

random.seed(42)

stores = []
store_ids = []

region_area_df = pd.read_csv("data_generation/raw_data/region_areas.csv")


def get_random_region_area():
    row = region_area_df.sample(n=1).iloc[0]
    return row["region"], row["area"]


def get_region_from_area(area):
    row = region_area_df[region_area_df["area"] == area]
    if row.empty:
        print(f"Unknown {area}!")
    else:
        return row.iloc[0]["region"]


for i in range(1, NUM_PHYSICAL_STORES + 1):
    store_id = f"STOR{i:03d}"
    store_ids.append(store_id)

    if random.random() < 0.8:
        mall = random.choice(list(MALL_TO_AREA.keys()))
        area = MALL_TO_AREA[mall]
        region = get_region_from_area(area)
        store_name = f"MegaMart {mall}"
        MALL_TO_AREA.pop(mall)
        store_type = "Mall"

    else:
        block_no = random.randint(100, 999)
        region, area = get_random_region_area()
        store_name = f"MegaMart Blk {block_no} {area} Street"
        store_type = "Neighborhood"

    stores.append(
        {
            "store_id": store_id,
            "store_name": store_name,
            "area": area,
            "region": region,
            "store_type": store_type,
        }
    )

stores.append(
    {
        "store_id": f"STOR{NUM_PHYSICAL_STORES + 1:03d}",
        "store_name": "MegaMart Online",
        "area": "Nationwide",
        "region": "Nationwide",
        "store_type": "Online",
    }
)

df_stores = pd.DataFrame(stores)
df_stores.to_csv("data_generation/raw_data/stores_raw.csv", index=False)
print("stores_raw.csv file generated")
