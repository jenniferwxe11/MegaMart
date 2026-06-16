import pandas as pd

# --- BUNDLE PRICINGS ---


def test_bundle_pricings_dates(dataframes):
    df = dataframes["bundle_pricings"].copy()
    assert (
        pd.to_datetime(df["effective_start_date"])
        <= pd.to_datetime(df["effective_end_date"])
    ).all()


def test_bundle_pricings_discount_value_less_than_bundle_price(dataframes):
    df = dataframes["bundle_pricings"].copy()
    assert (df["discount_value"] <= df["bundle_price"]).all()


def test_bundle_pricings_non_overlapping_per_bundle(dataframes):
    """
    No two pricing rows for the same bundle should have overlapping date ranges.
    """
    df = dataframes["bundle_pricings"].copy()
    df["effective_start_date"] = pd.to_datetime(df["effective_start_date"])
    df["effective_end_date"] = pd.to_datetime(df["effective_end_date"])
    for bundle_id, group in df.groupby("bundle_id"):
        rows = group.sort_values("effective_start_date").reset_index(drop=True)
        for i in range(len(rows) - 1):
            assert (
                rows.loc[i, "effective_end_date"]
                < rows.loc[i + 1, "effective_start_date"]
            ), f"Overlapping pricing periods for bundle {bundle_id}"


# --- PROMOTIONS ---


def test_promotion_dates(dataframes):
    df = dataframes["promotions"].copy()
    assert (
        pd.to_datetime(df["effective_start_date"])
        <= pd.to_datetime(df["effective_end_date"])
    ).all()


def test_promotion_percentage_discount_at_most_100(dataframes):
    """
    Percentage discounts should not exceed 100%.
    """
    df = dataframes["promotions"]
    pct = df[df["promotion_mechanic"] == "percentage_discount"]
    assert (pct["promotion_value"] <= 100).all()


def test_promotion_bundle_scope_has_bundle_target(dataframes):
    """
    Bundle promotions must reference a valid bundle_id as their target.
    """
    promotions = dataframes["promotions"].copy()
    bundles = dataframes["bundles"].copy()
    valid_bundles = set(bundles["bundle_id"].unique())
    bundle_promos = promotions[promotions["promotion_mechanic"] == "bundle"]
    for _, row in bundle_promos.iterrows():
        assert (
            row["promotion_target_id"] in valid_bundles
        ), f"Promotion {row['promotion_id']} references unknown bundle {row['promotion_target_id']}"


def test_promotion_product_scope_has_product_target(dataframes):
    """
    Product scoped promotions must reference a valid product_id as their target.
    """
    promotions = dataframes["promotions"].copy()
    products = dataframes["products"].copy()
    valid_pids = set(products["product_id"].unique())
    product_promos = promotions[promotions["promotion_scope"] == "product"]
    for _, row in product_promos.iterrows():
        assert (
            row["promotion_target_id"] in valid_pids
        ), f"Promotion {row['promotion_id']} references unknown product {row['promotion_target_id']}"
