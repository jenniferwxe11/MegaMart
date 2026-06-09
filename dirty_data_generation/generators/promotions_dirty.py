from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    inject_nulls,
)
from dirty_data_generation.utils.io_utils import save


@register("dirty_promotions")
def dirty_promotions(ctx: GenerationContext):
    df = ctx.promotions.promotions_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # Promotion value = 0 for non free shipping rows
    not_fs = df["promotion_mechanic"] != "free_shipping"
    zero_v = df[not_fs].sample(frac=0.03, random_state=20).index
    df.loc[zero_v, "promotion_value"] = [0 for _ in range(len(zero_v))]
    append_error(df, zero_v, "zero promotion value for non-free-shipping")

    # End date before start date
    inv_idx = df.sample(frac=0.02, random_state=21).index
    df.loc[inv_idx, ["effective_start_date", "effective_end_date"]] = df.loc[
        inv_idx, ["effective_end_date", "effective_start_date"]
    ].values
    append_error(df, inv_idx, "inverted date range")

    # Null promotion_value
    mask = df[["promotion_mechanic", "promotion_scope"]].notna().all(axis=1)

    df = inject_nulls(
        df, mask, "promotion_value", rate=0.02, error_label="missing promotion value"
    )

    # Scope/mechanic mismatch: free_shipping on scope = product
    fs_idx = (
        df[df["promotion_mechanic"] == "free_shipping"]
        .sample(frac=0.02, random_state=23)
        .index
    )
    df.loc[fs_idx, "promotion_scope"] = "product"
    append_error(df, fs_idx, "free shipping promotion with product scope")

    # Duplicate promotion_id
    dup_idx = df.sample(frac=0.01, random_state=24).index
    replacement_ids = (
        df["promotion_id"].sample(n=len(dup_idx), replace=True, random_state=25).values
    )
    df.loc[dup_idx, "promotion_id"] = replacement_ids
    append_error(df, dup_idx, "duplicate promotion id")

    # Negative min_spend
    ms_idx = df[df["min_spend"].notna()].sample(frac=0.01, random_state=25).index
    df.loc[ms_idx, "min_spend"] = -abs(df.loc[ms_idx, "min_spend"])
    append_error(df, ms_idx, "negative min spend")

    return save(df, "promotions_dirty.csv")
