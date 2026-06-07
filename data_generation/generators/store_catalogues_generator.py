import random
from typing import Any
import pandas as pd
from data_generation.config.generation_config import LIMIT_STORE_CATALOGUES
from data_generation.config.store_products_config import (
    STORE_TYPE_CONFIG,
    NATURAL_NAME_VARIATION_RATE,
    NATURAL_BRAND_VARIATION_RATE,
)
from data_generation.services.products.store_catalogue_service import (
    inject_name_error,
    inject_brand_error,
)
from data_generation.utils.io_utils import save
from data_generation.registry import register
from data_generation.context.generation_context import GenerationContext

@register("store_catalogues_generator")
def store_catalogues_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    stores_df = ctx.stores.stores_df
    products_df = ctx.products.products_df
    store_ids = ctx.stores.store_ids
    product_ids = ctx.products.product_ids
    essential_product_ids = ctx.products.essential_product_ids
    non_essential_product_ids = ctx.products.non_essential_product_ids
    
    # ---------------------------
    # Storage
    # ---------------------------

    store_catalogues: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    for store_id in store_ids:

        if len(store_catalogues) >= LIMIT_STORE_CATALOGUES:
            break
        
        store_type = stores_df.loc[stores_df["store_id"] == store_id, "store_type"].iloc[0]

        # Determine store assortment size based on store type
        assort_low, assort_high = STORE_TYPE_CONFIG[store_type]["Assortment"]
        total_products = int(len(product_ids) * random.uniform(assort_low, assort_high))

        # Ensure essential categories are always stocked
        essen_low, essen_high = STORE_TYPE_CONFIG[store_type]["Essential"]
        essential_count = min(
            int(total_products * random.uniform(essen_low, essen_high)),
            len(essential_product_ids),
        )
        selected_essentials = random.sample(essential_product_ids, essential_count)

        # Simulate store assortment diversity
        remaining_slots = max(total_products - essential_count, 0)
        selected_non_essentials = random.sample(
            non_essential_product_ids,
            min(remaining_slots, len(non_essential_product_ids)),
        )
        selected_product = selected_essentials + selected_non_essentials

        for product_id in selected_product:
            product_match = products_df.loc[
                products_df["product_id"] == product_id
            ]

            if product_match.empty:
                continue

            product_row = product_match.iloc[0]
            product_name = product_row["product_name"]
            brand = product_row["brand"]
            category = product_row["category"]
            selling_price = product_row["selling_price"]

            # Natural store-level name/brand variation only.
            store_product_name = (
                inject_name_error(product_name)
                if random.random() < NATURAL_NAME_VARIATION_RATE
                else product_name
            )
            store_brand = (
                inject_brand_error(brand)
                if random.random() < NATURAL_BRAND_VARIATION_RATE
                else brand
            )

            # --- Store Product Listing Record ---
            store_catalogues.append(
                {
                    "store_id": store_id,
                    "product_id": product_id,
                    "store_product_name": store_product_name,
                    "store_brand": store_brand,
                    "store_category": category,
                    "store_selling_price": selling_price,
                }
            )

    # ---------------------------
    # Export to CSV
    # ---------------------------

    df_store_catalogues = pd.DataFrame(store_catalogues)
    df_store_catalogues = df_store_catalogues.sort_values(
        by=["store_id", "product_id"]
    ).reset_index(drop=True)
    save(df_store_catalogues, "store_catalogues_raw.csv")
