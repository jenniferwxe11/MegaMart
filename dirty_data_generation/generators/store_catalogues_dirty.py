import random

from data_generation.config.products_config import CATEGORIES
from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    MAX_ERRORS_PER_ROW,
    duplicate_rows,
    inject_whitespace,
)
from dirty_data_generation.utils.io_utils import save


@register("dirty_store_catalogues")
def dirty_store_catalogues(ctx: GenerationContext):
    df = ctx.store_catalogues.store_catalogues_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    store_product_price_map = ctx.store_catalogues.store_product_price_map

    for i, row in df.iterrows():
        current_errors = df.at[i, "error_types"]
        n_errors = len(set(current_errors))

        if n_errors >= MAX_ERRORS_PER_ROW:
            continue

        base = store_product_price_map.get(
            row["product_id"], row["store_selling_price"]
        )

        # Price spike: >40% above master
        if random.random() < 0.05 and n_errors < MAX_ERRORS_PER_ROW:
            df.at[i, "store_selling_price"] = round(base * random.uniform(1.4, 2.5), 2)
            df.at[i, "error_types"].append("price anomaly")
            n_errors += 1

        # Price crash: <50% of master (only if no price error already)
        elif (
            random.random() < 0.03
            and "price anomaly" not in df.at[i, "error_types"]
            and n_errors < MAX_ERRORS_PER_ROW
        ):
            df.at[i, "store_selling_price"] = round(base * random.uniform(0.1, 0.49), 2)
            df.at[i, "error_types"].append("price anomaly")
            n_errors += 1

        # Category label drift
        if (
            random.random() < 0.06
            and "category label drift" not in df.at[i, "error_types"]
            and n_errors < MAX_ERRORS_PER_ROW
        ):
            df.at[i, "store_category"] = random.choice(CATEGORIES)
            df.at[i, "error_types"].append("category label drift")
            n_errors += 1

        # Missing store_selling_price
        # Only inject if no price anomaly already on this row
        if (
            random.random() < 0.02
            and "price anomaly" not in df.at[i, "error_types"]
            and "missing store selling price" not in df.at[i, "error_types"]
            and n_errors < MAX_ERRORS_PER_ROW
        ):
            df.at[i, "store_selling_price"] = None
            df.at[i, "error_types"].append("missing store selling price")

    # Whitespace/casing in store_product_name
    df = inject_whitespace(
        df,
        col="store_product_name",
        rate=0.07,
        error_label="store product name formatting anomaly",
        max_errors=MAX_ERRORS_PER_ROW,
    )

    # Duplicate (store_id, product_id) listings
    df = duplicate_rows(
        df,
        rate=0.03,
        error_label="duplicate listing",
    )

    return save(df, "store_catalogues_dirty.csv")
