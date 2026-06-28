import pandas as pd

# --- CUSTOMERS ---


def test_customer_output_dob_less_than_signup_date(ctx):
    df = ctx.customers.customers_df
    mask = df["dob"].notna() & df["signup_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "dob"])
        <= pd.to_datetime(df.loc[mask, "signup_date"])
    ).all()


def test_customer_output_dob_not_in_future(ctx):
    df = ctx.customers.customers_df
    assert (
        df["dob"].isna()
        | (pd.to_datetime(df["dob"], errors="coerce") <= pd.Timestamp.now())
    ).all()


def test_customer_output_signup_date_not_in_future(ctx):
    df = ctx.customers.customers_df
    assert (
        df["signup_date"].isna()
        | (pd.to_datetime(df["signup_date"], errors="coerce") <= pd.Timestamp.now())
    ).all()


def test_customer_output_at_least_18_at_signup(ctx):
    df = ctx.customers.customers_df
    signup_date = pd.to_datetime(df["signup_date"], errors="coerce")
    dob = pd.to_datetime(df["dob"], errors="coerce")
    minimum_allowed_dob = signup_date - pd.DateOffset(years=18)

    assert (signup_date.isna() | dob.isna() | (dob <= minimum_allowed_dob)).all()


def test_customer_output_online_omnichannel_customers_have_email(ctx):
    """
    Online Only and Omnichannel customers should have an email address.
    """
    df = ctx.customers.customers_df
    online_types = {"Online Only", "Omnichannel"}
    online = df[df["customer_type"].isin(online_types)]
    assert online["email"].notna().all(), "Online/Omnichannel customer missing email"


def test_customer_output_online_omnichannel_customers_have_device_info(ctx):
    """
    Online Only and Omnichannel customers should have device category and platform.
    """
    df = ctx.customers.customers_df
    online_types = {"Online Only", "Omnichannel"}
    online = df[df["customer_type"].isin(online_types)]
    assert online["device_category"].notna().all()
    assert online["device_platform"].notna().all()


def test_customer_output_retail_walk_in_no_signup_date(ctx):
    """
    Retail Walk-In customers should not have signup_date.
    """
    df = ctx.customers.customers_df
    walkin = df[df["customer_type"] == "Retail Walk-In"]
    assert (
        walkin["signup_date"].isna().all()
    ), "Retail Walk-In customer has unexpected signup_date"
