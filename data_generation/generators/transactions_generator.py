import json
import random
from collections import Counter
from typing import Any

import pandas as pd
from faker import Faker

from data_generation.config.generation_config import (
    LIMIT_TRANSACTION_ITEMS,
    NUM_TRANSACTIONS,
)
from data_generation.config.transactions_config import (
    CUSTOMER_TYPE_DISTRIBUTION,
    PAYMENT_CONFIG,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.clickstreams.clickstream_session_service import (
    generate_timestamp,
)
from data_generation.services.transactions.transaction_cart_service import (
    generate_cart_items,
)
from data_generation.services.transactions.transaction_lookup_service import (
    get_shipping_fee,
    get_store,
)
from data_generation.services.transactions.transaction_promotion_service import (
    apply_cart_level_discount,
    get_eligible_promotions,
    opt_for_delivery,
    resolve_promotion_stack,
    select_shipping_promo,
    should_use_promo,
)
from data_generation.utils.io_utils import save

fake = Faker()


@register("transactions_generator")
def transactions_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    DATA_START_DATE = ctx.config.DATA_START_DATE
    DATA_END_DATE = ctx.config.DATA_END_DATE
    customers_df = ctx.customers.customers_df
    customer_ids = ctx.customers.customer_ids
    customer_type_to_ids_map = ctx.customers.customer_type_to_ids_map
    customer_segment_map = ctx.customers.customer_segment_map
    online_store_id = ctx.stores.online_store_id
    product_name_map = ctx.products.product_name_map
    product_price_map = ctx.products.product_price_map
    product_category_map = ctx.products.product_category_map

    assert ctx.clickstreams is not None
    clickstreams_df = ctx.clickstreams.clickstreams_df
    payment_success = ctx.clickstreams.payment_success

    # ---------------------------
    # Storage
    # ---------------------------

    transactions: list[dict[str, Any]] = []
    transaction_items: list[dict[str, Any]] = []

    # -------------------------------
    # Generation: Online Transactions
    # -------------------------------

    if clickstreams_df.empty or "session_id" not in clickstreams_df.columns:
        session_groups = {}
    else:
        session_groups = {
            sid: df.reset_index(drop=True)
            for sid, df in clickstreams_df.groupby("session_id", sort=False)
        }

    i = 1
    for _, pay_row in payment_success.iterrows():

        if (
            len(transactions) >= NUM_TRANSACTIONS
            and len(transaction_items) >= LIMIT_TRANSACTION_ITEMS
        ):
            break

        transaction_id = f"TRAN{i:03d}"
        local_transaction_items = []

        # Get session details
        session_id = pay_row["session_id"]
        customer_id = pay_row["customer_id"]
        timestamp = pd.Timestamp(pay_row["timestamp"].replace(microsecond=0))
        customer_segment = pay_row["customer_segment"]

        session_events = session_groups.get(session_id)
        if session_events is None:
            continue

        payment_rows = session_events[
            session_events["event_type"] == "Payment Successful"
        ]
        if payment_rows.empty:
            continue

        payment_method = random.choices(
            PAYMENT_CONFIG["Online"]["methods"],
            weights=PAYMENT_CONFIG["Online"]["weights"],
        )[0]

        # Reconstruct cart from clickstream
        purchased_items = pay_row.get("purchased_items", [])
        if isinstance(purchased_items, str):
            try:
                purchased_items = json.loads(purchased_items.replace("'", '"'))
            except (json.JSONDecodeError, TypeError):
                purchased_items = []

        cart_counts = Counter(purchased_items)
        cart_items = []

        # Each product in cart is recorded as a separate transaction row
        for product_id, quantity in cart_counts.items():
            product_price = product_price_map.get(product_id)
            if product_price is None:
                continue

            category = product_category_map.get(product_id)
            product_name = product_name_map.get(product_id, "Unknown Product")

            cart_items.append(
                {
                    "product_id": product_id,
                    "name": product_name,
                    "price": product_price,
                    "category": category,
                    "quantity": quantity,
                }
            )

        if not cart_items:
            continue

        channel = "Online"

        # --- Cart Subtotal ---
        cart_subtotal = sum(item["price"] * item["quantity"] for item in cart_items)

        # --- Promotion Selection ---
        eligible_promotions = get_eligible_promotions(
            ctx, timestamp, cart_items, cart_subtotal
        )

        non_shipping_promos = [
            p for p in eligible_promotions if p["promotion_mechanic"] != "free_shipping"
        ]

        stacked = resolve_promotion_stack(
            ctx,
            customer_segment,
            non_shipping_promos,
            cart_items,
            timestamp,
            cart_subtotal,
            channel,
        )

        # Online: user chooses to apply (70% chance each)
        selected_promotions = [p for p in stacked if random.random() < 0.7]

        # --- Promotion Discount ---
        total_discount = 0
        final_allocation: dict[str, int | float] = {}
        promotion_allocations = []

        for promo in selected_promotions:
            discount, allocation = apply_cart_level_discount(
                ctx,
                cart_items,
                promo["promotion_id"],
                timestamp,
            )
            total_discount += discount

            # Store item level discount allocation
            promotion_allocations.append(
                {
                    "promotion_id": promo["promotion_id"],
                    "promotion_mechanic": promo["promotion_mechanic"],
                    "discount": discount,
                    "allocation": allocation,
                }
            )

            # Aggregate total discount allocation
            for k, v in allocation.items():
                if v is None:
                    continue

                final_allocation[k] = final_allocation.get(k, 0) + v

        # Guard: remove invalid discounts
        if total_discount <= 0:
            total_discount = 0
            promotion_allocations = []
            final_allocation = {}

        # --- Shipping Discount ---
        shipping_discount = 0
        shipping_fee = get_shipping_fee(ctx, online_store_id, customer_id)

        shipping_promo = select_shipping_promo(eligible_promotions, cart_subtotal)

        if shipping_promo and random.random() < should_use_promo(
            customer_segment, cart_subtotal
        ):
            shipping_discount = shipping_fee
            promotion_allocations.append(
                {
                    "promotion_id": shipping_promo["promotion_id"],
                    "promotion_mechanic": shipping_promo["promotion_mechanic"],
                    "discount": shipping_discount,
                    "allocation": {},
                }
            )

        # --- Transaction Items ---
        # Each product in cart is recorded as a separate transaction row
        for item in cart_items:
            product_id = item["product_id"]
            product_name = item["name"]
            product_price = item["price"]
            category = item["category"]
            quantity = item["quantity"]

            item_subtotal = product_price * quantity

            # Prevent over allocation
            item_discount = min(final_allocation.get(product_id, 0), item_subtotal)

            total_amount = max(0, item_subtotal - item_discount)

            # Store In Store Item Transaction Record
            local_transaction_items.append(
                {
                    "transaction_id": transaction_id,
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "quantity": quantity,
                    "unit_price": round(product_price, 2),
                    "item_subtotal": round(item_subtotal, 2),
                    "item_discount": round(item_discount, 2),
                    "final_item_price": round(total_amount, 2),
                }
            )

        # --- Reconcile Totals ---
        items_total = sum(item["final_item_price"] for item in local_transaction_items)

        ground_truth = cart_subtotal - total_discount
        drift = ground_truth - items_total

        if local_transaction_items and abs(drift) > 0:
            last = local_transaction_items[-1]
            last["final_item_price"] += drift

        # Recompute after drift correction
        items_total = sum(item["final_item_price"] for item in local_transaction_items)

        transaction_total = items_total + shipping_fee - shipping_discount

        diff = abs(
            (cart_subtotal - total_discount + shipping_fee - shipping_discount)
            - (items_total + shipping_fee - shipping_discount)
        )

        if diff > 0.01:
            print("MISMATCH:", diff)
            print("transaction_id:", transaction_id)

        basket_size = sum(item["quantity"] for item in cart_items)
        num_unique_items = len(cart_items)

        # Zero out financials on failure
        # if order_status == "Failed":
        #     total_discount = 0
        #     transaction_total = 0
        #     shipping_discount = 0
        #     promotion_allocations = []
        #     final_allocation = {}

        #     # Remove generated transaction items
        #     local_transaction_items = []

        transaction_items.extend(local_transaction_items)

        transactions.append(
            {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "store_id": online_store_id,
                "transaction_time": timestamp,
                "cart_subtotal": round(cart_subtotal, 2),
                "total_discount": round(total_discount, 2),
                "shipping_fee": round(shipping_fee, 2),
                "shipping_discount": round(shipping_discount, 2),
                "transaction_total": round(transaction_total, 2),
                "payment_method": payment_method,
                "basket_size": basket_size,
                "num_unique_items": num_unique_items,
                "applied_promotions": [
                    {
                        "promotion_id": promo["promotion_id"],
                        "promotion_type": promo["promotion_mechanic"],
                        "amount": float(round(promo["discount"], 2)),
                    }
                    for promo in promotion_allocations
                    if promo["discount"] > 0
                ],
            }
        )
        i += 1

    # ---------------------------------
    # Generation: In Store Transactions
    # ---------------------------------

    while len(transactions) < NUM_TRANSACTIONS:

        if len(transaction_items) >= LIMIT_TRANSACTION_ITEMS:
            break

        transaction_id = f"TRAN{i:03d}"
        local_transaction_items = []

        # --- Construct Transaction Details ---
        customer_type = random.choices(
            list(CUSTOMER_TYPE_DISTRIBUTION.keys()),
            weights=list(CUSTOMER_TYPE_DISTRIBUTION.values()),
            k=1,
        )[0]

        # Sample customers based on customer type distribution
        candidates = customer_type_to_ids_map.get(customer_type, [])
        customer_id = (
            random.choice(candidates) if candidates else random.choice(customer_ids)
        )

        customer_segment = customer_segment_map.get(customer_id, None)

        store_id = get_store(ctx, customer_id)

        signup_date = customers_df.loc[
            customers_df["customer_id"] == customer_id, "signup_date"
        ].iloc[0]

        signup_date = pd.Timestamp(signup_date)

        if pd.isna(signup_date):
            signup_date = pd.Timestamp(DATA_START_DATE)

        # Simulate transaction timestamp with seasonality
        transaction_time = pd.Timestamp(
            generate_timestamp(
                ctx, pd.Timestamp(signup_date), pd.Timestamp(DATA_END_DATE)
            )
        )

        payment_method = random.choices(
            PAYMENT_CONFIG["In Store"]["methods"],
            weights=PAYMENT_CONFIG["In Store"]["weights"],
        )[0]

        # Cart construction
        cart_items = []
        while not cart_items:
            cart_items = generate_cart_items(
                ctx,
                customer_segment,
                store_id,
            )

        channel = "In Store"

        # --- Cart Subtotal ---
        cart_subtotal = sum(item["price"] * item["quantity"] for item in cart_items)

        # --- Promotion Selection ---
        eligible_promotions = get_eligible_promotions(
            ctx, transaction_time, cart_items, cart_subtotal
        )

        non_shipping_promos = [
            p for p in eligible_promotions if p["promotion_mechanic"] != "free_shipping"
        ]

        stacked = resolve_promotion_stack(
            ctx,
            customer_segment,
            non_shipping_promos,
            cart_items,
            transaction_time,
            cart_subtotal,
            channel,
        )

        selected_promotions = stacked

        # --- Promotion Discount ---
        total_discount = 0
        final_allocation = {}
        promotion_allocations = []

        for promo in selected_promotions:
            discount, allocation = apply_cart_level_discount(
                ctx,
                cart_items,
                promo["promotion_id"],
                transaction_time,
            )
            total_discount += discount

            # Store item level discount allocation
            promotion_allocations.append(
                {
                    "promotion_id": promo["promotion_id"],
                    "promotion_mechanic": promo["promotion_mechanic"],
                    "discount": discount,
                    "allocation": allocation,
                }
            )

            # Aggregate total discount allocation
            for k, v in allocation.items():
                if v is None:
                    continue

                final_allocation[k] = final_allocation.get(k, 0) + v

        # Guard: remove invalid discounts
        if total_discount <= 0:
            total_discount = 0
            promotion_allocations = []
            final_allocation = {}

        # --- Shipping Discount ---
        shipping_discount = 0
        shipping_fee = 0

        shipping_promo = select_shipping_promo(eligible_promotions, cart_subtotal)

        # Decide whether or not the user will ship the groceries
        will_ship = opt_for_delivery(
            ctx, customer_id, store_id, shipping_promo, cart_subtotal
        )
        if will_ship:
            shipping_fee = get_shipping_fee(ctx, store_id, customer_id)

        if shipping_promo is not None and shipping_fee > 0:
            if random.random() < should_use_promo(customer_segment, cart_subtotal):
                shipping_discount = shipping_fee
                promotion_allocations.append(
                    {
                        "promotion_id": shipping_promo["promotion_id"],
                        "promotion_mechanic": shipping_promo["promotion_mechanic"],
                        "discount": shipping_discount,
                        "allocation": {},
                    }
                )

        # --- Transaction Items ---
        # Each product in cart is recorded as a separate transaction row
        for item in cart_items:
            product_id = item["product_id"]
            product_name = item["name"]
            product_price = item["price"]
            category = item["category"]
            quantity = item["quantity"]

            item_subtotal = product_price * quantity

            # Prevent over allocation
            item_discount = min(final_allocation.get(product_id, 0), item_subtotal)

            total_amount = max(0, item_subtotal - item_discount)

            # Store In Store Item Transaction Record
            local_transaction_items.append(
                {
                    "transaction_id": transaction_id,
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "quantity": quantity,
                    "unit_price": round(product_price, 2),
                    "item_subtotal": round(item_subtotal, 2),
                    "item_discount": round(item_discount, 2),
                    "final_item_price": round(total_amount, 2),
                }
            )

        # --- Reconcile Totals ---
        items_total = sum(item["final_item_price"] for item in local_transaction_items)

        ground_truth = cart_subtotal - total_discount
        drift = ground_truth - items_total

        if local_transaction_items and abs(drift) > 0:
            last = local_transaction_items[-1]
            last["final_item_price"] += drift

        # Recompute after drift correction
        items_total = sum(item["final_item_price"] for item in local_transaction_items)

        transaction_total = items_total + shipping_fee - shipping_discount

        diff = abs(
            (cart_subtotal - total_discount + shipping_fee - shipping_discount)
            - (items_total + shipping_fee - shipping_discount)
        )

        if diff > 0.01:
            print("MISMATCH:", diff)
            print("transaction_id:", transaction_id)

        basket_size = sum(item["quantity"] for item in cart_items)
        num_unique_items = len(cart_items)

        # Zero out financials on failure
        # if order_status == "Failed":
        #     cart_subtotal = 0
        #     total_discount = 0
        #     shipping_fee = 0
        #     transaction_total = 0
        #     shipping_discount = 0
        #     promotion_allocations = []
        #     final_allocation = {}

        #     # Remove generated transaction items
        #     local_transaction_items = []

        transaction_items.extend(local_transaction_items)

        transactions.append(
            {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "store_id": store_id,
                "transaction_time": transaction_time,
                "cart_subtotal": round(cart_subtotal, 2),
                "total_discount": round(total_discount, 2),
                "shipping_fee": round(shipping_fee, 2),
                "shipping_discount": round(shipping_discount, 2),
                "transaction_total": round(transaction_total, 2),
                "payment_method": payment_method,
                "basket_size": basket_size,
                "num_unique_items": num_unique_items,
                "applied_promotions": [
                    {
                        "promotion_id": promo["promotion_id"],
                        "promotion_type": promo["promotion_mechanic"],
                        "amount": float(round(promo["discount"], 2)),
                    }
                    for promo in promotion_allocations
                    if promo["discount"] > 0
                ],
            }
        )
        i += 1

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(transactions), "transactions_raw.csv")
    save(pd.DataFrame(transaction_items), "transaction_items_raw.csv")
