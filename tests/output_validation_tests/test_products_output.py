import pandas as pd

# --- PRODUCTS ---


def test_product_output_cost_price_less_than_selling_price(ctx):
    df = ctx.products.products_df
    assert (df["cost_price"] < df["selling_price"]).all()


# --- COMPETITOR PRICE HISTORY ---


def test_product_output_competitor_price_history_update_timestamp_not_in_future(ctx):
    df = ctx.competitor_products.competitor_price_history_df
    assert (pd.to_datetime(df["update_timestamp"]) <= pd.Timestamp.now()).all()


# --- PRODUCT LIFECYCLE ---


def test_product_output_lifecycle_launch_date_not_in_future(ctx):
    df = ctx.product_lifecycles.product_lifecycles_df
    assert (pd.to_datetime(df["launch_date"]) <= pd.Timestamp.now()).all()


def test_product_output_lifecycle_discontinuation_date_after_launch_date(ctx):
    df = ctx.product_lifecycles.product_lifecycles_df
    mask = df["discontinuation_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "discontinuation_date"])
        >= pd.to_datetime(df.loc[mask, "launch_date"])
    ).all()


def test_product_output_lifecycle_discontinued_has_discontinuation_date(ctx):
    df = ctx.product_lifecycles.product_lifecycles_df
    assert (df["discontinuation_date"].notna() | (df["status"] != "Discontinued")).all()


def test_product_output_lifecycle_valid_from_after_launch_date(ctx):
    df = ctx.product_lifecycles.product_lifecycles_df
    assert (pd.to_datetime(df["valid_from"]) >= pd.to_datetime(df["launch_date"])).all()


def test_product_output_lifecycle_valid_to_after_valid_from(ctx):
    df = ctx.product_lifecycles.product_lifecycles_df
    mask = df["valid_to"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "valid_to"])
        >= pd.to_datetime(df.loc[mask, "valid_from"])
    ).all()


def test_product_output_lifecycle_is_current_no_valid_to(ctx):
    df = ctx.product_lifecycles.product_lifecycles_df
    assert (~df["is_current"] | df["valid_to"].isna()).all()


def test_product_output_lifecycle_exactly_one_current_per_product(ctx):
    """
    Each product should have exactly one 'is_current=True' lifecycle row.
    """
    df = ctx.product_lifecycles.product_lifecycles_df
    current_counts = df[df["is_current"]].groupby("product_id").size()
    assert (
        current_counts == 1
    ).all(), "Some products have multiple or zero current lifecycle rows"


def test_product_output_lifecycle_non_overlapping_validity(ctx):
    """
    Validity periods for the same product must not overlap.
    """
    df = ctx.product_lifecycles.product_lifecycles_df
    df["valid_from"] = pd.to_datetime(df["valid_from"])
    df["valid_to"] = pd.to_datetime(df["valid_to"])
    for pid, group in df.groupby("product_id"):
        rows = group.sort_values("valid_from").reset_index(drop=True)
        for i in range(len(rows) - 1):
            vto = rows.loc[i, "valid_to"]
            vnext = rows.loc[i + 1, "valid_from"]
            if pd.notna(vto):
                assert vto <= vnext, f"Overlapping validity periods for product {pid}"


# --- PRODUCT CONTENT QUALITY ---


def test_product_output_content_quality_image_logic(ctx):
    df = ctx.product_content_quality.product_content_quality_df
    assert ((df["image_count"] > 0) | ~df["has_image"]).all()


def test_product_output_content_quality_description(ctx):
    df = ctx.product_content_quality.product_content_quality_df
    assert ((df["description_length"] > 0) | ~df["has_description"]).all()


def test_product_output_content_quality_valid_from_not_in_future(ctx):
    df = ctx.product_content_quality.product_content_quality_df
    assert (pd.to_datetime(df["valid_from"]) <= pd.Timestamp.now()).all()


def test_product_output_content_quality_valid_to(ctx):
    df = ctx.product_content_quality.product_content_quality_df
    mask = df["valid_to"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "valid_to"])
        >= pd.to_datetime(df.loc[mask, "valid_from"])
    ).all()


def test_product_output_content_quality_is_current(ctx):
    df = ctx.product_content_quality.product_content_quality_df
    assert (~df["is_current"] | df["valid_to"].isna()).all()


def test_product_output_content_quality_exactly_one_current_per_product(ctx):
    df = ctx.product_content_quality.product_content_quality_df
    current_counts = df[df["is_current"]].groupby("product_id").size()
    assert (
        current_counts == 1
    ).all(), "Some products have multiple current content quality rows"


def test_product_output_content_quality_tier_consistent_with_score(ctx):
    """
    Excellent tier should have higher image_quality_score than Poor tier.
    """
    df = ctx.product_content_quality.product_content_quality_df
    excellent_min = df[df["quality_tier"] == "Excellent"]["image_quality_score"].min()
    poor_max = df[df["quality_tier"] == "Poor"]["image_quality_score"].max()
    if pd.notna(excellent_min) and pd.notna(poor_max):
        assert (
            excellent_min > poor_max
        ), "Excellent tier quality scores overlap with Poor tier"


# --- PRODUCT REVIEWS ---


def test_product_output_reviews_not_in_future(ctx):
    df = ctx.product_reviews.product_reviews_df
    assert (pd.to_datetime(df["review_date"]) <= pd.Timestamp.now()).all()
