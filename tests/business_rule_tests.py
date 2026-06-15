import pandas as pd

now = pd.Timestamp.now()

# --- CUSTOMERS ---


def test_customer_dob_less_than_signup_date(dataframes):
    df = dataframes["customers"]
    mask = df["dob"].notna() & df["signup_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "dob"])
        <= pd.to_datetime(df.loc[mask, "signup_date"])
    ).all()


def test_customer_dob_not_in_future(dataframes):
    df = dataframes["customers"]
    assert (
        df["dob"].isna() | (pd.to_datetime(df["dob"], errors="coerce") <= now)
    ).all()


def test_customer_signup_date_not_in_future(dataframes):
    df = dataframes["customers"]
    assert (
        df["signup_date"].isna()
        | (pd.to_datetime(df["signup_date"], errors="coerce") <= now)
    ).all()


# --- PRODUCTS ---


def test_cost_price_less_than_selling_price(dataframes):
    df = dataframes["products"]
    assert (df["cost_price"] < df["selling_price"]).all()


# --- COMPETITOR PRICE HISTORY ---


def test_competitor_price_history_update_timestamp_not_in_future(dataframes):
    df = dataframes["competitor_price_history"]
    assert (pd.to_datetime(df["update_timestamp"]) <= now).all()


# --- PRODUCT LIFECYCLE ---


def test_product_lifecycle_launch_date_not_in_future(dataframes):
    df = dataframes["product_lifecycles"]
    assert (pd.to_datetime(df["launch_date"]) <= now).all()


def test_product_lifecycle_discontinuation_date(dataframes):
    df = dataframes["product_lifecycles"]
    mask = df["discontinuation_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "discontinuation_date"])
        >= pd.to_datetime(df.loc[mask, "launch_date"])
    ).all()
    assert (df["discontinuation_date"].notna() | (df["status"] != "Discontinued")).all()


def test_product_lifecycle_valid_from(dataframes):
    df = dataframes["product_lifecycles"]
    assert (pd.to_datetime(df["valid_from"]) >= pd.to_datetime(df["launch_date"])).all()


def test_product_lifecycle_valid_to(dataframes):
    df = dataframes["product_lifecycles"]
    mask = df["valid_to"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "valid_to"])
        >= pd.to_datetime(df.loc[mask, "valid_from"])
    ).all()


def test_product_lifecycle_is_current(dataframes):
    df = dataframes["product_lifecycles"]
    assert (~df["is_current"] | df["valid_to"].isna()).all()


# --- PRODUCT CONTENT QUALITY ---


def test_product_content_quality_image_logic(dataframes):
    df = dataframes["product_content_quality"]
    assert ((df["image_count"] > 0) | ~df["has_image"]).all()


def test_product_content_quality_description(dataframes):
    df = dataframes["product_content_quality"]
    assert ((df["description_length"] > 0) | ~df["has_description"]).all()


def test_product_content_quality_valid_from_not_in_future(dataframes):
    df = dataframes["product_content_quality"]
    assert (pd.to_datetime(df["valid_from"]) <= now).all()


def test_product_content_quality_valid_to(dataframes):
    df = dataframes["product_content_quality"]
    mask = df["valid_to"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "valid_to"])
        >= pd.to_datetime(df.loc[mask, "valid_from"])
    ).all()


def test_product_content_quality_is_current(dataframes):
    df = dataframes["product_content_quality"]
    assert (~df["is_current"] | df["valid_to"].isna()).all()


# --- STOCKOUT EVENTS ---


def test_stockout_events_stockout_start_date_not_in_future(dataframes):
    df = dataframes["stockout_events"]
    assert (pd.to_datetime(df["stockout_start_date"]) <= now).all()


def test_stockout_events_dates(dataframes):
    df = dataframes["stockout_events"]
    mask = df["stockout_end_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "stockout_end_date"])
        >= pd.to_datetime(df.loc[mask, "stockout_start_date"])
    ).all()


# --- STOCK SNAPSHOTS ---


def test_stock_snapshots_stock_band_status_match(dataframes):
    df = dataframes["stock_snapshots"]
    assert (
        ((df["stock_band"] == "0") & (df["stock_status"] == "Out of Stock"))
        | ((df["stock_band"] == "1-5") & (df["stock_status"] == "Limited Stock"))
        | ((df["stock_band"] == "6-20") & (df["stock_status"] == "Low Stock"))
        | ((df["stock_band"] == "21-100") & (df["stock_status"] == "In Stock"))
        | ((df["stock_band"] == "101+") & (df["stock_status"] == "Overstocked"))
    ).all()


def test_stock_snapshots_week_start_date_not_in_future(dataframes):
    df = dataframes["stock_snapshots"]
    assert (pd.to_datetime(df["week_start_date"]) <= now).all()


# --- INVENTORY CHANGE EVENTS ---


def test_inventory_change_event_event_timestamp_not_in_future(dataframes):
    df = dataframes["inventory_change_events"]
    assert (pd.to_datetime(df["event_timestamp"]) <= now).all()


# --- CAMPAIGNS ---


def test_campaign_dates(dataframes):
    df = dataframes["campaigns"]
    assert (pd.to_datetime(df["start_date"]) <= pd.to_datetime(df["end_date"])).all()


def test_campaign_status_aligned_with_dates(dataframes):
    df = dataframes["campaigns"]
    assert (
        (df["status"] != "Completed") | (pd.to_datetime(df["end_date"]) <= now)
    ).all()


# --- CAMPAIGN EXPOSURE ---


def test_campaign_exposure_exposed_time(dataframes):
    df = dataframes["campaign_exposures"]
    mask = df["exposed_time"].notna()
    assert (pd.to_datetime(df.loc[mask, "exposed_time"]) <= now).all()
    assert (df["exposed_time"].notna() | ~df["exposed"]).all()


def test_campaign_exposure_opened(dataframes):
    df = dataframes["campaign_exposures"]
    assert (~df["opened"] | df["exposed"]).all()


def test_campaign_exposure_opened_time(dataframes):
    df = dataframes["campaign_exposures"]
    mask_notna = df["opened_time"].notna()
    assert (pd.to_datetime(df.loc[mask_notna, "opened_time"]) <= now).all()
    assert (df["opened_time"].notna() | ~df["opened"]).all()
    mask_both = df["opened_time"].notna() & df["exposed_time"].notna()
    assert (
        pd.to_datetime(df.loc[mask_both, "opened_time"])
        >= pd.to_datetime(df.loc[mask_both, "exposed_time"])
    ).all()


def test_campaign_exposure_clicked(dataframes):
    df = dataframes["campaign_exposures"]
    assert (
        ~df["clicked"]
        | df["opened"]
        | df["channel"].isin(["Paid Advertisements", "In-App"])
    ).all()


def test_campaign_exposure_clicked_time(dataframes):
    df = dataframes["campaign_exposures"]
    mask_notna = df["clicked_time"].notna()
    assert (pd.to_datetime(df.loc[mask_notna, "clicked_time"]) <= now).all()
    assert (df["clicked_time"].notna() | ~df["clicked"]).all()
    mask_both = df["clicked_time"].notna() & df["opened_time"].notna()
    assert (
        pd.to_datetime(df.loc[mask_both, "clicked_time"])
        >= pd.to_datetime(df.loc[mask_both, "opened_time"])
    ).all()


# --- BUNDLE PRICINGS ---


def test_bundle_pricings_dates(dataframes):
    df = dataframes["bundle_pricings"]
    assert (
        pd.to_datetime(df["effective_start_date"])
        <= pd.to_datetime(df["effective_end_date"])
    ).all()


def test_bundle_pricings_discount_value_less_than_bundle_price(dataframes):
    df = dataframes["bundle_pricings"]
    assert (df["discount_value"] <= df["bundle_price"]).all()


# --- PROMOTIONS ---


def test_promotion_dates(dataframes):
    df = dataframes["promotions"]
    assert (
        pd.to_datetime(df["effective_start_date"])
        <= pd.to_datetime(df["effective_end_date"])
    ).all()


# --- CLICKSTREAMS ---


def test_clickstream_has_treatment_campaign(dataframes):
    df = dataframes["clickstreams"]
    assert (
        ~df["has_treatment_campaign"]
        | df["campaign_ids"].apply(lambda x: x is not None and len(x) > 0)
    ).all()


def test_clickstream_event_timestamp_not_in_future(dataframes):
    df = dataframes["clickstreams"]
    assert (pd.to_datetime(df["event_timestamp"]) <= now).all()


def test_clickstream_bounce_flag(dataframes):
    df = dataframes["clickstreams"]
    assert ((df["bounce_flag"] == 0) | (df["event_order"] == 1)).all()


def test_clickstream_purchased_items(dataframes):
    df = dataframes["clickstreams"]
    assert (
        df["purchased_items"].apply(lambda x: x is not None and len(x) > 0)
        | (df["event_type"] != "Payment Successful")
    ).all()


# --- TRANSACTIONS ---


def test_transaction_total_discount_value_calculation(dataframes):
    df = dataframes["transactions"]
    no_promo = df["applied_promotions"].apply(len) == 0
    assert (~no_promo | (df["total_discount"] == 0)).all()


def test_transaction_time_not_in_future(dataframes):
    df = dataframes["transactions"]
    assert (pd.to_datetime(df["transaction_time"]) <= now).all()


def test_transaction_total_discount_less_than_cart_subtotal(dataframes):
    df = dataframes["transactions"]
    assert (df["total_discount"] < df["cart_subtotal"]).all()


def test_transaction_shipping_discount_less_than_or_equal_to_shipping_fee(dataframes):
    df = dataframes["transactions"]
    assert (df["shipping_discount"] <= df["shipping_fee"]).all()


def test_transaction_num_unique_items_less_than_or_equal_to_basket_size(dataframes):
    df = dataframes["transactions"]
    assert (df["num_unique_items"] <= df["basket_size"]).all()


# --- TRANSACTION ITEMS ---


def test_transaction_items_item_subtotal_value_calculation(dataframes):
    df = dataframes["transaction_items"]
    assert (abs(df["item_subtotal"] - (df["unit_price"] * df["quantity"])) < 0.01).all()


def test_transaction_item_discount_less_than_item_subtotal(dataframes):
    df = dataframes["transaction_items"]
    assert (df["item_discount"] < df["item_subtotal"]).all()


# --- PRODUCT REVIEWS ---


def test_product_reviews_not_in_future(dataframes):
    df = dataframes["product_reviews"]
    assert (pd.to_datetime(df["review_date"]) <= now).all()
