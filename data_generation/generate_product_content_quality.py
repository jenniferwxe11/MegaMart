import random
from datetime import date
import pandas as pd
from pandas import isna
from config import DATA_END_DATE, QUALITY_UPDATE_POLICY
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

products_df = pd.read_csv("data_generation/raw_data/products_raw.csv")
product_ids = products_df["product_id"].dropna().tolist()

product_lifecycles_df = pd.read_csv("data_generation/raw_data/product_lifecycles_raw.csv")
product_lifecycles_df.loc[:, "launch_date"] = pd.to_datetime(
    product_lifecycles_df.get("launch_date"), errors="coerce"
)
product_lifecycles_df.loc[:, "discontinuation_date"] = pd.to_datetime(
    product_lifecycles_df.get("discontinuation_date"), errors="coerce"
)

category_attributes_df = pd.read_csv("data_generation/raw_data/category_attributes_raw.csv")

product_content_quality = []

for product_id in product_ids:
    product_lifecycle = product_lifecycles_df.loc[product_lifecycles_df["product_id"] == product_id, "status"].iloc[0]

    # get expected attribute count of category
    category = products_df.loc[products_df["product_id"] == product_id, "category"].iloc[0]
    category_attributes = category_attributes_df.loc[category_attributes_df["category"] == category, "attribute"].dropna().tolist()
    total_attributes = len(category_attributes)

    if product_lifecycle == "New":
        quality_tier = "poor"
    else:
        quality_tier = random.choices(
            ["poor", "average", "good", "excellent"],
            weights=[0.2, 0.4, 0.3, 0.1],
            k=1
        )[0]
    
    if quality_tier == "poor":
        has_image = random.random() < 0.4
        image_count = random.randint(0, 1) if has_image else 0
        image_quality_score = round(random.uniform(0.1, 0.4),2)
        has_nutritional_info = random.random() < 0.3
        has_description = random.random() < 0.5
        description_length = random.randint(10, 50) if has_description else 0
        missing_attribute_count = random.randint(
            int(0.5 * total_attributes), total_attributes
        )

    elif quality_tier == "average":
        has_image = True
        image_count = random.randint(1, 3)
        image_quality_score = round(random.uniform(0.4, 0.7),2)
        has_nutritional_info = random.random() < 0.6
        has_description = True
        description_length = random.randint(50, 120)
        missing_attribute_count = random.randint(
            int(0.2 * total_attributes), int(0.5 * total_attributes)
        )

    elif quality_tier == "good":
        has_image = True
        image_count = random.randint(3, 5)
        image_quality_score = round(random.uniform(0.7, 0.9),2)
        has_nutritional_info = random.random() < 0.8
        has_description = True
        description_length = random.randint(120, 250)
        missing_attribute_count = random.randint(
                    0, int(0.2 * total_attributes)
                )

    else:
        has_image = True
        image_count = random.randint(5, 8)
        image_quality_score = round(random.uniform(0.9, 1.0),2)
        has_nutritional_info = True
        has_description = True
        description_length = random.randint(250, 500)
        missing_attribute_count = 0

    launch_date = product_lifecycles_df.loc[product_lifecycles_df["product_id"] == product_id, "launch_date"].iloc[0]
    launch_date = launch_date.date()
    discontinuation_date = product_lifecycles_df.loc[product_lifecycles_df["product_id"] == product_id, "discontinuation_date"].iloc[0]
    discontinuation_date = (
        discontinuation_date.date() if not isna(discontinuation_date) else None
    )

    if discontinuation_date is not None:
        end_date = discontinuation_date
    else:
        end_date = DATA_END_DATE
    
    recent_bias_years = QUALITY_UPDATE_POLICY[quality_tier]
    
    if recent_bias_years is not None:
        biased_start = max(
            launch_date,
            date(end_date.year - recent_bias_years, 1, 1)
        )
        last_updated = fake.date_between(
            start_date=biased_start,
            end_date=end_date
        )

    else:
        last_updated = launch_date

    product_content_quality.append(
        {
            "product_id": product_id,
            "has_image": has_image,
            "image_count": image_count,
            "image_quality_score": image_quality_score,
            "has_nutritional_info": has_nutritional_info,
            "has_description": has_description,
            "description_length": description_length,
            "missing_attribute_count": missing_attribute_count,
            "last_updated": last_updated,
        }
    )

df_product_content_quality = pd.DataFrame(product_content_quality)
df_product_content_quality.to_csv("data_generation/raw_data/product_content_quality_raw.csv", index=False)
print("product_content_quality_raw.csv file generated")
