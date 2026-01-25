import json
import random
from datetime import datetime

import pandas as pd
from config import NUM_TRANSACTIONS
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

transactions = []
transaction_ids = []

customers_df = pd.read_csv(
    "data_generation/raw_data/customers_raw.csv", parse_dates=["signup_date"]
)
customers_df.loc[:, "signup_date"] = pd.to_datetime(
    customers_df["signup_date"], errors="coerce"
)
customer_ids = customers_df["customer_id"].dropna().tolist()

products_df = pd.read_csv("data_generation/raw_data/products_raw.csv")
product_ids = products_df["product_id"].dropna().tolist()

stores_df = pd.read_csv("data_generation/raw_data/stores_raw.csv")
store_ids = stores_df["store_id"].dropna().tolist()

campaigns_df = pd.read_csv("data_generation/raw_data/campaigns_raw.csv")
campaigns_df.loc[:, "start_date"] = pd.to_datetime(
    campaigns_df["start_date"], errors="coerce"
)
campaigns_df.loc[:, "end_date"] = pd.to_datetime(
    campaigns_df["end_date"], errors="coerce"
)
campaigns_df.loc[:, "is_ab_test"] = campaigns_df["is_ab_test"].astype(bool)

campaign_assignment_df = pd.read_csv(
    "data_generation/raw_data/campaign_assignments_raw.csv"
)

clickstreams_df = pd.read_csv(
    "data_generation/raw_data/clickstreams_raw.csv", parse_dates=["timestamp"]
)
clickstreams_df.loc[:, "timestamp"] = pd.to_datetime(
    clickstreams_df["timestamp"], errors="coerce"
)
region_area_df = pd.read_csv("data_generation/raw_data/region_areas.csv")

LOCATIONS = region_area_df["area"].tolist()


def get_payment_status(session_events, timestamp):
    after_payment_events = session_events[
        session_events["timestamp"] >= timestamp
    ].sort_values("timestamp")
    if "Payment Successful" in after_payment_events["event_type"].values:
        return True
    return False


def get_store_id():
    return "STOR006"


def get_shipping_cost():
    return 15


def get_product_details(product_id, timestamp):
    product_row = products_df[products_df["product_id"] == product_id]
    if product_row.empty:
        return None, None, None, None
    row = product_row.iloc[0]

    product_name = row["product_name"]
    price = float(row["selling_price"])
    discount_applied = 0.0
    stock = row["stock_quantity"]

    if (
        row["status"] == "Promotion"
        and pd.notna(row["promotion_start_date"])
        and pd.notna(row["promotion_end_date"])
        and row["promotion_start_date"] <= timestamp <= row["promotion_end_date"]
        and pd.notna(row["discount_percentage"])
    ):
        discount_applied = float(row["discount_percentage"])
    return product_name, price, discount_applied, stock


def get_existing_campaign(customer_id, timestamp):
    existing_campaigns = []
    campaign_ids = campaign_assignment_df[
        campaign_assignment_df["customer_id"] == customer_id
    ]["campaign_id"]

    for campaign_id in campaign_ids:
        row = campaigns_df[campaigns_df["campaign_id"] == campaign_id]
        if row.empty:
            continue

        start_date = row["start_date"].iloc[0]
        end_date = row["end_date"].iloc[0]

        if (
            pd.notna(start_date)
            and pd.notna(end_date)
            and start_date <= timestamp <= end_date
        ):
            existing_campaigns.append(campaign_id)

    return existing_campaigns


def get_campaign_promotion(campaign_id):
    row = campaigns_df[campaigns_df["campaign_id"] == campaign_id]
    if row.empty:
        return None, None
    discount_type = row["discount_type"].iloc[0]
    discount_percentage = row["discount_percentage"].iloc[0]
    return discount_type, discount_percentage


# only get clickstream with events "Payment Attempt"
payment_attempts = clickstreams_df[clickstreams_df["event_type"] == "Payment Attempt"]

# for omnichannel/online only customers
i = 1
for _, pay_row in payment_attempts.iterrows():
    transaction_id = f"TRAN{i:03d}"
    transaction_ids.append(transaction_id)

    # get session details
    session_id = pay_row["session_id"]
    customer_id = pay_row["customer_id"]
    store_id = get_store_id()
    timestamp = pay_row["timestamp"]
    timestamp = timestamp.replace(microsecond=0)

    # get payment details
    session_events = clickstreams_df[clickstreams_df["session_id"] == session_id]
    payment_status = get_payment_status(session_events, timestamp)

    # parse cart content if stored as string
    cart_content = pay_row["cart_content"]
    if isinstance(cart_content, str):
        try:
            cart_content = json.loads(cart_content.replace("'", '"'))
        except (json.JSONDecodeError, TypeError):
            cart_content = []

    if payment_status:

        # find existing campaign promotions
        existing_campaigns = get_existing_campaign(customer_id, timestamp)
        campaign_id = existing_campaigns[0] if existing_campaigns else None

        discount_type, discount_percentage = None, 0.0
        if campaign_id:
            discount_type, discount_percentage = get_campaign_promotion(campaign_id)

        # create a transaction row per product in cart
        for product_id in cart_content:
            product_name, product_price, discount_applied, stock = get_product_details(
                product_id, timestamp
            )

            quantity = 1
            subtotal = product_price * quantity

            if discount_applied:
                discount_amount = subtotal * discount_applied
                discount_amount = round(discount_amount, 2)
            else:
                discount_amount = 0

            total_amount = subtotal - discount_amount

            transactions.append(
                {
                    "transaction_id": transaction_id,
                    "customer_id": customer_id,
                    "store_id": store_id,
                    "product_id": product_id,
                    "transaction_time": timestamp,
                    "product_name": product_name,
                    "quantity": quantity,
                    "price": product_price,
                    "discount_applied": discount_amount,
                    "total_amount": total_amount,
                    "payment_method": "Online",
                    "order_status": "Completed",
                    "campaign_id": campaign_id,
                }
            )
    i += 1

# for in-store customers
for _ in range(1, NUM_TRANSACTIONS + 1):
    transaction_id = f"TRAN{i:03d}"
    transaction_ids.append(transaction_id)

    customer_id = random.choice(customer_ids)
    signup_date = customers_df.loc[
        customers_df["customer_id"] == customer_id, "signup_date"
    ].iloc[0]
    if pd.isna(signup_date):
        signup_date = datetime(2024, 1, 1)

    campaign_id = None
    transaction_time = fake.date_time_between(
        start_date=signup_date, end_date=datetime(2024, 12, 31)
    )
    transaction_time = transaction_time.replace(microsecond=0)
    store_id = random.choice(store_ids + [None, ""])
    payment_method = random.choices(["Credit Card", "Cash"], weights=[0.6, 0.4], k=1)[0]

    no_of_products = random.randint(1, 25)
    product_ids_copy = product_ids.copy()
    product_ids_copy = product_ids_copy + [None, ""]

    for _ in range(no_of_products):
        product_id = random.choice(product_ids_copy)
        product_ids_copy.remove(product_id)

        if product_id is None or product_id == "":
            product_name = None
            product_price = None
        else:
            product_name, product_price, discount_applied, stock = get_product_details(
                product_id, transaction_time
            )

        base_quantity = random.randint(1, 5)

        try:
            subtotal = float(product_price) * int(base_quantity)
            if random.random() < 0.05:
                discount_percentage = random.uniform(0, 0.2)
                discount_amount = subtotal * discount_percentage
                discount_amount = round(discount_amount, 2)
                total_amount = subtotal - discount_amount
            else:
                total_amount = subtotal
                discount_amount = 0
        except (ValueError, TypeError):
            subtotal = None
            discount_amount = None
            total_amount = None

        if total_amount is not None:
            total_amount = round(total_amount, 2)

        order_status = random.choices(
            ["Completed", "Refunded"], weights=[0.93, 0.07], k=1
        )[0]

        transactions.append(
            {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "store_id": store_id,
                "product_id": product_id,
                "transaction_time": transaction_time,
                "product_name": product_name,
                "quantity": base_quantity,
                "price": product_price,
                "discount_applied": discount_amount,
                "total_amount": total_amount,
                "payment_method": payment_method,
                "order_status": order_status,
                "campaign_id": campaign_id,
            }
        )

    i += 1

df_transactions = pd.DataFrame(transactions)
df_transactions.to_csv("data_generation/raw_data/transactions_raw.csv", index=False)
print("transactions_raw.csv file generated")
