import pandas as pd

# --- PRODUCTS ---


def test_cost_price_less_than_selling_price(dataframes):
    df = dataframes["products"].copy()
    assert (df["cost_price"] < df["selling_price"]).all()


# --- COMPETITOR PRICE HISTORY ---


def test_competitor_price_history_update_timestamp_not_in_future(dataframes):
    df = dataframes["competitor_price_history"]
    assert (pd.to_datetime(df["update_timestamp"]) <= pd.Timestamp.now()).all()


# --- PRODUCT LIFECYCLE ---


def test_product_lifecycle_launch_date_not_in_future(dataframes):
    df = dataframes["product_lifecycles"].copy()
    assert (pd.to_datetime(df["launch_date"]) <= pd.Timestamp.now()).all()


def test_product_lifecycle_discontinuation_date_after_launch_date(dataframes):
    df = dataframes["product_lifecycles"].copy()
    mask = df["discontinuation_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "discontinuation_date"])
        >= pd.to_datetime(df.loc[mask, "launch_date"])
    ).all()


def test_product_lifecycle_discontinued_has_discontinuation_date(dataframes):
    df = dataframes["product_lifecycles"].copy()
    assert (df["discontinuation_date"].notna() | (df["status"] != "Discontinued")).all()


def test_product_lifecycle_valid_from_after_launch_date(dataframes):
    df = dataframes["product_lifecycles"].copy()
    assert (pd.to_datetime(df["valid_from"]) >= pd.to_datetime(df["launch_date"])).all()


def test_product_lifecycle_valid_to_after_valid_from(dataframes):
    df = dataframes["product_lifecycles"].copy()
    mask = df["valid_to"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "valid_to"])
        >= pd.to_datetime(df.loc[mask, "valid_from"])
    ).all()


def test_product_lifecycle_is_current_no_valid_to(dataframes):
    df = dataframes["product_lifecycles"].copy()
    assert (~df["is_current"] | df["valid_to"].isna()).all()


def test_product_lifecycle_exactly_one_current_per_product(dataframes):
    """
    Each product should have exactly one 'is_current=True' lifecycle row.
    """
    df = dataframes["product_lifecycles"].copy()
    current_counts = df[df["is_current"]].groupby("product_id").size()
    assert (
        current_counts == 1
    ).all(), "Some products have multiple or zero current lifecycle rows"


def test_product_lifecycle_non_overlapping_validity(dataframes):
    """
    Validity periods for the same product must not overlap.
    """
    df = dataframes["product_lifecycles"].copy()
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


def test_product_content_quality_image_logic(dataframes):
    df = dataframes["product_content_quality"].copy()
    assert ((df["image_count"] > 0) | ~df["has_image"]).all()


def test_product_content_quality_description(dataframes):
    df = dataframes["product_content_quality"].copy()
    assert ((df["description_length"] > 0) | ~df["has_description"]).all()


def test_product_content_quality_valid_from_not_in_future(dataframes):
    df = dataframes["product_content_quality"].copy()
    assert (pd.to_datetime(df["valid_from"]) <= pd.Timestamp.now()).all()


def test_product_content_quality_valid_to(dataframes):
    df = dataframes["product_content_quality"].copy()
    mask = df["valid_to"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "valid_to"])
        >= pd.to_datetime(df.loc[mask, "valid_from"])
    ).all()


def test_product_content_quality_is_current(dataframes):
    df = dataframes["product_content_quality"].copy()
    assert (~df["is_current"] | df["valid_to"].isna()).all()


def test_product_content_quality_exactly_one_current_per_product(dataframes):
    df = dataframes["product_content_quality"].copy()
    current_counts = df[df["is_current"]].groupby("product_id").size()
    assert (
        current_counts == 1
    ).all(), "Some products have multiple current content quality rows"


def test_product_content_quality_tier_consistent_with_score(dataframes):
    """
    Excellent tier should have higher image_quality_score than Poor tier.
    """
    df = dataframes["product_content_quality"].copy()
    excellent_min = df[df["quality_tier"] == "Excellent"]["image_quality_score"].min()
    poor_max = df[df["quality_tier"] == "Poor"]["image_quality_score"].max()
    if pd.notna(excellent_min) and pd.notna(poor_max):
        assert (
            excellent_min > poor_max
        ), "Excellent tier quality scores overlap with Poor tier"


# --- PRODUCT REVIEWS ---


def test_product_reviews_not_in_future(dataframes):
    df = dataframes["product_reviews"].copy()
    assert (pd.to_datetime(df["review_date"]) <= pd.Timestamp.now()).all()
