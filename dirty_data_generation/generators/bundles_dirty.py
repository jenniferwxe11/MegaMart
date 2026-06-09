from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    duplicate_rows,
    inject_nulls,
    inject_whitespace,
)
from dirty_data_generation.utils.io_utils import save


@register("dirty_bundles")
def dirty_bundles(ctx: GenerationContext):
    bdf = ctx.bundles.bundles_df.copy()

    bdf["error_types"] = [[] for _ in range(len(bdf))]

    # Mixed-case/whitespace in bundle name
    bdf = inject_whitespace(
        bdf, col="bundle_name", rate=0.02, error_label="bundle name formatting anomaly"
    )

    # Duplicate bundle_id
    dup_idx = bdf.sample(frac=0.02, random_state=40).index
    replacement_ids = (
        bdf["bundle_id"].sample(n=len(dup_idx), replace=True, random_state=40).values
    )
    bdf.loc[dup_idx, "bundle_id"] = replacement_ids
    append_error(bdf, dup_idx, "duplicate bundle id")

    return save(bdf, "bundles_dirty.csv")


@register("dirty_bundle_pricings")
def dirty_bundle_pricings(ctx: GenerationContext):
    bpdf = ctx.bundles.bundle_pricings_df.copy()

    bpdf["error_types"] = [[] for _ in range(len(bpdf))]

    # Negative discount value
    neg_idx = (
        bpdf[bpdf["discount_value"].notna()].sample(frac=0.03, random_state=41).index
    )
    bpdf.loc[neg_idx, "discount_value"] = -abs(bpdf.loc[neg_idx, "discount_value"])
    append_error(bpdf, neg_idx, "negative discount value")

    # Null discount
    bpdf = inject_nulls(
        bpdf,
        bpdf["discount_value"].notna(),
        "discount_value",
        rate=0.02,
        error_label="missing discount value",
    )

    # effective_end_date < effective_start_date
    inv_idx = bpdf.sample(frac=0.02, random_state=43).index
    for idx in inv_idx:
        bpdf.loc[idx, ["effective_start_date", "effective_end_date"]] = bpdf.loc[
            idx, ["effective_end_date", "effective_start_date"]
        ].values
    append_error(bpdf, inv_idx, "inverted date range")

    # Duplicate pricing rows
    bpdf = duplicate_rows(
        bpdf,
        rate=0.03,
    )

    return save(bpdf, "bundle_pricings_dirty.csv")
