import pandas as pd
from config import CATEGORY_ATTRIBUTES

category_attribute = []

for category, attributes in CATEGORY_ATTRIBUTES.items():
    for attribute in attributes:
        category_attribute.append(
        {
            "category": category,
            "attribute": attribute,
        }
)
    
df_category_attributes = pd.DataFrame(category_attribute)
df_category_attributes.to_csv("data_generation/raw_data/category_attributes_raw.csv", index=False)
print("category_attributes.csv file generated")
