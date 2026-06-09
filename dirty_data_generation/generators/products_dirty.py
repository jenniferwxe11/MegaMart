import random

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    inject_nulls,
    inject_whitespace,
)
from dirty_data_generation.utils.io_utils import save


@register("dirty_products")
def dirty_products(ctx: GenerationContext):
    df = ctx.products.products_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # Selling price = 0 or negative
    zero_idx = df.sample(frac=0.02, random_state=10).index
    df.loc[zero_idx, "selling_price"] = [
        random.choice([0, -abs(random.uniform(1, 50))]) for _ in range(len(zero_idx))
    ]
    append_error(df, zero_idx, "zero or negative selling price")

    # Cost > selling price
    inv_idx = df.sample(frac=0.03, random_state=11).index
    df.loc[inv_idx, "cost_price"] = [
        df.loc[idx, "selling_price"] * random.uniform(1.1, 1.5) for idx in inv_idx
    ]
    append_error(df, inv_idx, "margin inversion")

    # Extreme outlier price
    out_idx = df.sample(frac=0.01, random_state=12).index
    df.loc[out_idx, "selling_price"] = [
        round(random.uniform(10000, 1000000), 2) for _ in range(len(out_idx))
    ]
    append_error(df, out_idx, "extreme outlier price")

    # Missing brand
    df = inject_nulls(
        df, df["brand"].isna(), "brand", rate=0.03, error_label="missing brand"
    )

    # Name case/whitespace noise
    df = inject_whitespace(
        df, col="product_name", rate=0.06, error_label="product name formatting anomaly"
    )

    # Duplicate product name (same name, different ID)
    dup_names = df.sample(frac=0.02, random_state=13)

    df.loc[dup_names.index, "product_name"] = (
        df["product_name"].sample(n=len(dup_names), random_state=14).values
    )

    append_error(df, dup_names.index, "duplicate product name")

    return save(df, "products_dirty.csv")
