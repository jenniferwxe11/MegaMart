import random
from datetime import timedelta
from typing import Any

import pandas as pd

from data_generation.config.competitor_products_config import COMPETITORS
from data_generation.config.generation_config import (
    LIMIT_COMPETITOR_PRICE_HISTORY,
    LIMIT_COMPETITOR_PRODUCTS,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.competitor_products.competitor_product_service import (
    get_competitor_products,
    get_scrape_batches,
)
from data_generation.utils.io_utils import save


@register("competitor_products_generator")
def competitor_products_generator(ctx: GenerationContext):
    # ---------------------------
    # Storage
    # ---------------------------

    competitor_price_history: list[dict[str, Any]] = []
    all_competitor_products: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    for competitor, configuration in COMPETITORS.items():

        if (
            len(all_competitor_products) >= LIMIT_COMPETITOR_PRODUCTS
            or len(competitor_price_history) >= LIMIT_COMPETITOR_PRICE_HISTORY
        ):
            break

        # --- Build Competitor Product Catalogue ---
        generated_products = get_competitor_products(ctx, competitor, configuration)
        for product in generated_products:

            product_name = product.get("scraped_product_name")
            if not product_name or str(product_name).strip() == "":
                continue

            # Store Clickstream Product Catalogue Record
            all_competitor_products.append(
                {
                    "competitor": competitor,
                    "product_id": product["product_id"],
                    "product_name": product["scraped_product_name"],
                    "brand": product["brand"],
                    "category": product["category"],
                    "is_exclusive": product["is_exclusive"],
                }
            )

        # --- Generate Competitor Price History ---
        scrape_batches = get_scrape_batches(ctx)

        scraped_df = pd.DataFrame(generated_products)
        if scraped_df.empty:
            continue

        scraped_df = scraped_df[
            scraped_df["scraped_product_name"].notna()
            & (scraped_df["scraped_product_name"].str.strip() != "")
        ]

        if scraped_df.empty:
            continue

        for batch_date in scrape_batches:

            scraped_products = scraped_df.sample(
                frac=random.uniform(0.5, 0.8), replace=False
            )

            for _, product_row in scraped_products.iterrows():

                product_id = product_row["product_id"]

                scraped_category = product_row["category"]
                scraped_product_name = product_row["scraped_product_name"]

                if not scraped_product_name or str(scraped_product_name).strip() == "":
                    continue

                # Simulate minor intra day price fluctuations
                scraped_price = round(
                    product_row["selling_price"] * random.uniform(0.97, 1.03), 2
                )

                # Simulate promotional activity
                has_active_promo = random.random() < configuration["promo_rate"]
                if has_active_promo:
                    scraped_price = round(scraped_price * random.uniform(0.7, 0.9), 2)

                # Simulate staggered scraping jobs
                update_timestamp = batch_date + timedelta(
                    minutes=random.randint(0, 180)
                )

                # Store Competitor Pricing Record
                competitor_price_history.append(
                    {
                        "competitor": competitor,
                        "product_id": product_id,
                        "scraped_product_name": scraped_product_name,
                        "scraped_category": scraped_category,
                        "scraped_price": scraped_price,
                        "has_active_promo": has_active_promo,
                        "update_timestamp": update_timestamp,
                    }
                )

    # ---------------------------
    # Export to CSV
    # ---------------------------
    save(pd.DataFrame(all_competitor_products), "competitor_products_raw.csv")
    save(pd.DataFrame(competitor_price_history), "competitor_price_history_raw.csv")
