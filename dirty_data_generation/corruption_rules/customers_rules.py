# dirty_data_generation/corruption_rules/customers_rules.py

import random
from datetime import date

import pandas as pd
from faker import Faker

fake = Faker()

ONLINE_CUSTOMERS = [
    "Online Only",
    "Omnichannel",
]


# =============================================================================
# Missing Values
# =============================================================================


def missing_customer_name(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "customer_name"] = None


def missing_email(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "email"] = None


def missing_gender(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "gender"] = None


def missing_dob(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "dob"] = None


def missing_area(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "area"] = None


def missing_region(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "region"] = None


def missing_customer_segment(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "customer_segment"] = None


# =============================================================================
# Accepted Values
# =============================================================================


def invalid_gender(df, idx, ctx):

    if pd.isna(df.at[idx, "gender"]):
        return

    df.at[idx, "gender"] = random.choice(
        [
            "male",
            "female",
            "F",
            "M",
            "f",
            "m",
        ]
    )


def invalid_customer_type(df, idx, ctx):

    if pd.isna(df.at[idx, "customer_type"]):
        return

    df.at[idx, "customer_type"] = random.choice(
        [
            "VIP",
            "Guest",
            "Wholesale",
            "",
        ]
    )


def invalid_customer_segment(df, idx, ctx):

    if pd.isna(df.at[idx, "customer_segment"]):
        return

    df.at[idx, "customer_segment"] = random.choice(
        [
            "Premium",
            "Gold",
            "Inactive",
            "",
        ]
    )


def invalid_device_platform(df, idx, ctx):

    if pd.isna(df.at[idx, "device_platform"]):
        return

    df.at[idx, "device_platform"] = random.choice(
        [
            "Windows",
            "Linux",
            "Blackberry",
            "",
        ]
    )


def invalid_device_category(df, idx, ctx):

    if pd.isna(df.at[idx, "device_category"]):
        return

    df.at[idx, "device_category"] = random.choice(
        [
            "Laptop",
            "TV",
            "Console",
            "",
        ]
    )


# =============================================================================
# Formatting
# =============================================================================


def invalid_customer_id_format(df, idx, ctx):

    value = df.at[idx, "customer_id"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: x.replace("000", "00", 1),
        lambda x: x.replace("CUST", "CUST-", 1),
        lambda x: x.lower(),
        lambda x: x.replace("CUST", "C", 1),
        lambda x: x.replace("CUST", "CUS", 1),
        lambda x: x.replace("CUST", "CUST ", 1),
    ]

    df.at[idx, "customer_id"] = random.choice(corruptions)(value)


def invalid_customer_name(df, idx, ctx):

    value = df.at[idx, "customer_name"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: " " + x,
        lambda x: x + " ",
        lambda x: " " + x + " ",
    ]

    df.at[idx, "customer_name"] = random.choice(corruptions)(value)


def invalid_email_format(df, idx, ctx):

    value = df.at[idx, "email"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: x.replace(".com", "com", 1),
        lambda x: x.replace("@", "@@", 1),
        lambda x: x.rsplit(".", 1)[0] + ".",
        lambda x: x.replace("@", ".", 1),
        lambda x: x.replace("@", "@ ", 1),
        lambda x: x.replace(".com", ",com", 1),
    ]

    df.at[idx, "email"] = random.choice(corruptions)(value)


# =============================================================================
# Duplicates
# =============================================================================


def duplicate_email(df, idx, ctx):

    other_emails = df[df.index != idx]["email"].dropna().tolist()

    if not other_emails:
        return

    df.at[idx, "email"] = random.choice(other_emails)


def duplicate_customer_id(df, idx, ctx):

    other_customer_ids = df[df.index != idx]["customer_id"].dropna().tolist()

    if not other_customer_ids:
        return

    df.at[idx, "customer_id"] = random.choice(other_customer_ids)


# =============================================================================
# Business Rule Violations
# =============================================================================


def future_signup_date(df, idx, ctx):

    if pd.isna(df.at[idx, "signup_date"]):
        return

    df.at[idx, "signup_date"] = pd.Timestamp(fake.future_date("+5y"))


def invalid_dob(df, idx, ctx):

    if pd.isna(df.at[idx, "dob"]):
        return

    df.at[idx, "dob"] = random.choice(
        [
            fake.future_date("+5y"),
            fake.date_between(
                start_date=date(1800, 1, 1),
                end_date=date(1899, 12, 31),
            ),
        ]
    )


def signup_before_dob(df, idx, ctx):

    if pd.isna(df.at[idx, "signup_date"]) or pd.isna(df.at[idx, "dob"]):
        return

    df.at[idx, "signup_date"] = df.at[idx, "dob"] - pd.Timedelta(
        days=random.randint(30, 365)
    )


def underage_customer(df, idx, ctx):

    if pd.isna(df.at[idx, "signup_date"]):
        return

    df.at[idx, "dob"] = df.at[idx, "signup_date"] - pd.DateOffset(
        years=random.randint(10, 17)
    )


def area_region_mismatch(df, idx, ctx):
    """
    Valid area but assigned to the wrong region.
    """

    if pd.isna(df.at[idx, "area"]) or pd.isna(df.at[idx, "region"]):
        return

    area = df.at[idx, "area"]

    correct = ctx.region_areas.area_region_map.get(area)

    if correct is None:
        return

    wrong = [r for r in ctx.region_areas.regions if r != correct]

    df.at[idx, "region"] = random.choice(wrong)


def missing_email_marketing_preference(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "email_marketing_opt_in"] = None


def missing_sms_marketing_preference(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "sms_marketing_opt_in"] = None


def missing_push_notifications_preference(df, idx, ctx):

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "push_notifications_opt_in"] = None


def email_marketing_without_email(df, idx, ctx):
    """
    email_marketing_opt_in = TRUE
    while email = NULL
    """

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "email"] = None
    df.at[idx, "email_marketing_opt_in"] = True


def push_notifications_without_device_platform(df, idx, ctx):
    """
    Push notifications enabled
    but no device platform.
    """

    if df.at[idx, "customer_type"] not in ONLINE_CUSTOMERS:
        return

    df.at[idx, "push_notifications_opt_in"] = True
    df.at[idx, "device_platform"] = None


def missing_device_category(df, idx, ctx):
    """
    device_platform exists
    but device_category is missing.
    """

    if pd.isna(df.at[idx, "device_platform"]):
        return

    df.at[idx, "device_category"] = None
