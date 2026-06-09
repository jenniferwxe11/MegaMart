import random

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import append_error
from dirty_data_generation.utils.io_utils import save


@register("dirty_product_content")
def dirty_product_content(ctx: GenerationContext):
    df = ctx.product_content_quality.product_content_quality_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # has_image = False but image_count > 0
    no_img_idx = (
        df[~df["has_image"].astype(str).isin(["True", "true", True])]
        .sample(frac=0.03, random_state=100)
        .index
    )
    df.loc[no_img_idx, "image_count"] = [
        random.randint(1, 5) for _ in range(len(no_img_idx))
    ]
    append_error(df, no_img_idx, "has_image=False but image_count > 0")

    # image_quality_score > 1.0
    qs_idx = df.sample(frac=0.02, random_state=101).index
    df.loc[qs_idx, "image_quality_score"] = [
        round(random.uniform(1.01, 1.5), 2) for _ in range(len(qs_idx))
    ]
    append_error(df, qs_idx, "image_quality_score > 1.0")

    # description_length negative
    dl_idx = df.sample(frac=0.02, random_state=102).index
    df.loc[dl_idx, "description_length"] = [
        random.randint(-100, -1) for _ in range(len(dl_idx))
    ]
    append_error(df, dl_idx, "negative description length")

    # missing_attribute_count negative
    mac_idx = df.sample(frac=0.01, random_state=103).index
    df.loc[mac_idx, "missing_attribute_count"] = [
        random.randint(-10, -1) for _ in range(len(mac_idx))
    ]
    append_error(df, mac_idx, "negative missing attribute count")

    return save(df, "product_content_quality_dirty.csv")
