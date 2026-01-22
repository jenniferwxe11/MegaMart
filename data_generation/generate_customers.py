import random
from datetime import date

import pandas as pd
from config import MONTH_WEIGHTS_2024, NUM_CUSTOMERS, TARGET_SEGMENT
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

customers = []
customer_ids = []

region_area_df = pd.read_csv("data_generation/raw_data/region_areas.csv")


def get_random_region_area():
    row = region_area_df.sample(n=1).iloc[0]
    region, area = row["region"], row["area"]
    return region, area


def sample_signup_date_2024():
    month = random.choices(
        list(MONTH_WEIGHTS_2024.keys()), weights=list(MONTH_WEIGHTS_2024.values()), k=1
    )[0]

    # get valid day range
    if month == 2:
        day = random.randint(1, 29)  # 2024 is leap year
    elif month in {4, 6, 9, 11}:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 31)

    return date(2024, month, day)


dirty_rows = int(NUM_CUSTOMERS * 0.04)

for i in range(1, NUM_CUSTOMERS - dirty_rows + 1):
    cid = f"CUST{i:03d}"
    customer_ids.append(cid)

    # Customer type
    customer_type = random.choices(
        ["Retail Walk-In", "Retail Members", "Online Only", "Omnichannel"],
        weights=[0.6, 0.15, 0.15, 0.1],
        k=1,
    )[0]

    # Default values
    name = None
    email = None
    gender = None
    dob = None
    area = None
    region = None
    signup_date = None
    loyalty_points = None
    customer_segment = None
    email_marketing_opt_in = None
    sms_marketing_opt_in = None
    push_notifications_opt_in = None

    # Retail walk in has no customer information
    if customer_type != "Retail Walk-In":
        customer_segment = random.choices(
            list(TARGET_SEGMENT.keys()),
            weights=list(TARGET_SEGMENT.values()),
            k=1,
        )[0]

        # Retail members
        if customer_type == "Retail Members":
            email = f"{fake.user_name()}@{fake.safe_domain_name()}"
            signup_date = sample_signup_date_2024() if random.random() < 0.97 else None
            loyalty_points = 0

        # Online only customers
        elif customer_type == "Online Only":
            first_name = fake.first_name()
            last_name = fake.last_name()
            name = first_name + " " + last_name
            email = f"{first_name}.{last_name}@{fake.safe_domain_name()}".lower()
            gender = random.choice(["Female", "Male"])
            dob = fake.date_of_birth(minimum_age=18, maximum_age=85)
            region, area = get_random_region_area()
            signup_date = sample_signup_date_2024() if random.random() < 0.97 else None

            loyalty_points = 0

            email_opt_in = random.choices([True, False], weights=[0.28, 0.72], k=1)[0]

            sms_opt_in = random.choices([True, False], weights=[0.13, 0.87], k=1)[0]

            push_opt_in = random.choices([True, False], weights=[0.61, 0.39], k=1)[0]

        elif customer_type == "Omnichannel":
            first_name = fake.first_name()
            last_name = fake.last_name()
            name = first_name + " " + last_name
            email = f"{first_name}.{last_name}@{fake.safe_domain_name()}".lower()
            gender = random.choice(["Female", "Male"])
            dob = (
                fake.date_of_birth(minimum_age=18, maximum_age=85)
                if random.random() < 0.9
                else None
            )
            region, area = get_random_region_area()
            signup_date = sample_signup_date_2024() if random.random() < 0.97 else None
            loyalty_points = 0

            email_marketing_opt_in = random.choices(
                [True, False], weights=[0.28, 0.72], k=1
            )[0]

            sms_marketing_opt_in = random.choices(
                [True, False], weights=[0.13, 0.87], k=1
            )[0]

            push_notifications_opt_in = random.choices(
                [True, False], weights=[0.61, 0.39], k=1
            )[0]

    customers.append(
        {
            "customer_id": cid,
            "customer_type": customer_type,
            "customer_name": name,
            "email": email,
            "gender": gender,
            "dob": dob,
            "area": area,
            "region": region,
            "signup_date": signup_date,
            "loyalty_points": loyalty_points,
            "customer_segment": customer_segment,
            "email_marketing_opt_in": email_marketing_opt_in,
            "sms_marketing_opt_in": sms_marketing_opt_in,
            "push_notifications_opt_in": push_notifications_opt_in,
        }
    )

df_customers = pd.DataFrame(customers)
df_customers.to_csv("data_generation/raw_data/customers_raw.csv", index=False)
print("customers_raw.csv file generated")
