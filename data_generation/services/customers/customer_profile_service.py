import calendar
import random
from datetime import date

import pandas as pd
from faker import Faker

from data_generation.config.constants import (
    DATA_END_DATE,
    DATA_START_DATE,
)
from data_generation.config.customers_config import (
    DEVICE_CATEGORY,
    DEVICE_PLATFORM,
    SEASONAL_PEAK_MONTHS,
    TARGET_SEGMENT,
)
from data_generation.services.region_areas.region_area_service import (
    get_random_region_area,
)

fake = Faker()
USED_EMAILS = set()


def generate_unique_username_email():
    while True:
        email = f"{fake.user_name()}@{fake.safe_domain_name()}".lower()
        if email not in USED_EMAILS:
            USED_EMAILS.add(email)
            return email


def generate_unique_email(first_name, last_name):
    base = f"{first_name}.{last_name}".lower()

    while True:
        suffix = "" if random.random() < 0.7 else str(random.randint(1, 9999))
        email = f"{base}{suffix}@{fake.safe_domain_name()}"

        if email not in USED_EMAILS:
            USED_EMAILS.add(email)
            return email


def sample_signup_date():
    """
    Samples user sign up date within simulation date range.
    """
    year = random.randint(
        pd.Timestamp(DATA_START_DATE).year, pd.Timestamp(DATA_END_DATE).year
    )
    month = random.choices(
        list(SEASONAL_PEAK_MONTHS.keys()),
        weights=list(SEASONAL_PEAK_MONTHS.values()),
        k=1,
    )[0]

    # Get valid day range
    max_day = calendar.monthrange(year, month)[1]
    day = random.randint(1, max_day)

    sampled_date = date(year, month, day)

    if pd.Timestamp(sampled_date) < pd.Timestamp(DATA_START_DATE):
        return pd.Timestamp(DATA_START_DATE)
    if pd.Timestamp(sampled_date) > pd.Timestamp(DATA_END_DATE):
        return pd.Timestamp(DATA_END_DATE)

    return pd.Timestamp(sampled_date)


def generate_dob(signup_date):
    if signup_date is None:
        return None

    latest = signup_date - pd.DateOffset(years=18)
    earliest = signup_date - pd.DateOffset(years=85)

    return (
        fake.date_between(
            start_date=earliest.to_pydatetime().date(),
            end_date=latest.to_pydatetime().date(),
        )
        if random.random() < 0.9
        else None
    )


def generate_customer_profile(ctx, customer_type):
    """
    Generates a realistic customer profile based on the specified customer type.
    """

    # Initialize customer details
    name = None
    email = None
    gender = None
    dob = None
    area = None
    region = None
    signup_date = None
    customer_segment = None
    email_marketing_opt_in = None
    sms_marketing_opt_in = None
    push_notifications_opt_in = None
    device_category = None
    device_platform = None

    if customer_type != "Retail Walk-In":
        customer_segment = random.choices(
            list(TARGET_SEGMENT.keys()),
            weights=list(TARGET_SEGMENT.values()),
            k=1,
        )[0]

        # -------------------------------------
        # RETAIL MEMBERS:
        # - Primarily offline customers
        # - Limited digital footprint
        # - Basic profile (email + signup only)
        # -------------------------------------

        if customer_type == "Retail Members":
            email = generate_unique_username_email()
            signup_date = sample_signup_date() if random.random() < 0.97 else None

        # -----------------------------------------------------
        # ONLINE ONLY CUSTOMERS:
        # - Fully digital users with rich behavioural data
        # - Includes demographics, location, and device context
        # - Engagement driven by digital channels
        # -----------------------------------------------------

        elif customer_type == "Online Only":
            first_name = fake.first_name()
            last_name = fake.last_name()
            name = first_name + " " + last_name
            email = generate_unique_email(first_name, last_name)
            gender = random.choice(["Female", "Male"])
            region, area = get_random_region_area(ctx)
            signup_date = sample_signup_date()
            dob = generate_dob(signup_date)

            email_marketing_opt_in = random.choices(
                [True, False], weights=[0.28, 0.72], k=1
            )[0]
            sms_marketing_opt_in = random.choices(
                [True, False], weights=[0.13, 0.87], k=1
            )[0]
            push_notifications_opt_in = random.choices(
                [True, False], weights=[0.61, 0.39], k=1
            )[0]

            device_category = random.choices(
                list(DEVICE_CATEGORY.keys()),
                weights=list(DEVICE_CATEGORY.values()),
                k=1,
            )[0]

            device_platform = random.choices(
                list(DEVICE_PLATFORM[device_category].keys()),
                weights=list(DEVICE_PLATFORM[device_category].values()),
                k=1,
            )[0]

        # -------------------------------------------------
        # OMNICHANNEL CUSTOMERS:
        # - Engage across online and offline channels
        # - Partial data gaps reflect real-world conditions
        # - Key segment for integrated marketing strategies
        # -------------------------------------------------

        elif customer_type == "Omnichannel":
            first_name = fake.first_name()
            last_name = fake.last_name()
            name = first_name + " " + last_name
            email = generate_unique_email(first_name, last_name)
            gender = random.choice(["Female", "Male"])
            region, area = get_random_region_area(ctx)
            signup_date = sample_signup_date()
            dob = generate_dob(signup_date)

            email_marketing_opt_in = random.choices(
                [True, False], weights=[0.28, 0.72], k=1
            )[0]

            sms_marketing_opt_in = random.choices(
                [True, False], weights=[0.13, 0.87], k=1
            )[0]

            push_notifications_opt_in = random.choices(
                [True, False], weights=[0.61, 0.39], k=1
            )[0]

            device_category = random.choices(
                list(DEVICE_CATEGORY.keys()),
                weights=list(DEVICE_CATEGORY.values()),
                k=1,
            )[0]

            device_platform = random.choices(
                list(DEVICE_PLATFORM[device_category].keys()),
                weights=list(DEVICE_PLATFORM[device_category].values()),
                k=1,
            )[0]

    customer_profile = {
        "name": name,
        "email": email,
        "gender": gender,
        "dob": dob,
        "area": area,
        "region": region,
        "signup_date": signup_date,
        "customer_segment": customer_segment,
        "email_marketing_opt_in": email_marketing_opt_in,
        "sms_marketing_opt_in": sms_marketing_opt_in,
        "push_notifications_opt_in": push_notifications_opt_in,
        "device_category": device_category,
        "device_platform": device_platform,
    }

    return customer_profile
