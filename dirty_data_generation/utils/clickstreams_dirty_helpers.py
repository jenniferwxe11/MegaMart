import ast
import random
import uuid
from datetime import timedelta

import numpy as np
import pandas as pd
from faker import Faker

from data_generation.config.products_config import (
    CATEGORIES,
    CATEGORY_PRODUCT_DISTRIBUTION,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_search_term,
)
from dirty_data_generation.config.constants import MAX_ERRORS_PER_ROW

fake = Faker()


def clone_clean_row(row):
    return {k: v for k, v in row.items() if k != "error_types"} | {"error_types": []}


def assign_session_profile():
    return random.choices(
        ["clean", "light_noise", "moderate_noise", "heavy_corruption"],
        weights=[0.65, 0.2, 0.1, 0.05],
    )[0]


def assign_corruption_budget(intensity):
    if intensity == "clean":
        return 0
    elif intensity == "light_noise":
        return np.random.poisson(1)
    elif intensity == "moderate_noise":
        return np.random.poisson(2)
    else:
        return np.random.poisson(4)


def missing_fields(row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    # Missing fields
    field = random.choice(
        [
            "product_id",
            "category",
            "scroll_depth",
            "location",
            "cart_content",
            "cart_size",
            "timestamp",
            "event_order",
            "event_type",
            "page",
            "device_category",
        ]
    )

    row[field] = None
    row["error_types"].append(f"missing {field}")
    return row


def populate_fields(ctx, row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    product_ids = ctx.products.product_ids

    if row.get("scroll_depth") is None:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["scroll_depth"] = random.randint(0, 100)
            row["error_types"].append("populate scroll depth")

    if row.get("category") is None:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["category"] = random.choices(
                list(CATEGORY_PRODUCT_DISTRIBUTION.keys()),
                weights=list(CATEGORY_PRODUCT_DISTRIBUTION.values()),
                k=1,
            )[0]
            row["error_types"].append("populate category")

    if row.get("product_id") is None:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["product_id"] = random.choice(product_ids)
            row["error_types"].append("populate product id")

    if row.get("cart_size") is None:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["cart_size"] = random.randint(0, 20)
            row["error_types"].append("populate cart size")

    return row


def mismatch_fields(ctx, row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    product_ids = ctx.products.product_ids

    # Page/product_id mismatch
    if random.random() < 0.3 and row.get("event_type") in (
        "Product View",
        "Add to Cart",
        "Remove from Cart",
    ):
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["product_id"] = random.choice(product_ids)
            row["error_types"].append("mismatch product")

    # cart_size disagrees with cart_content length
    if random.random() < 0.3 and row.get("cart_size") is not None:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["cart_size"] = random.randint(0, 20)
            row["error_types"].append("mismatch cart size")

    if random.random() < 0.2 and row.get("scroll_depth") is not None:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["scroll_depth"] += random.uniform(-25, 25)
            row["error_types"].append("mismatch scroll depth")

    return row


def field_corruption(row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    # Scoll depth out of range
    if row.get("scroll_depth") is not None and random.random() < 0.2:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["scroll_depth"] = random.choice(
                [random.uniform(100.1, 150), random.uniform(-20, -0.1)]
            )
            row["error_types"].append("scroll out of bound")

    if row.get("category") is not None and random.random() < 0.3:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["category"] = fake.word()
            row["error_types"].append("category corruption")

    if row.get("bounce_flag") is not None and random.random() < 0.2:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["bounce_flag"] = "Bounced"
            row["error_types"].append("bounce flag corruption")

    if row.get("event_type") == "Checkout Start" and random.random() < 0.3:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["cart_size"] = 0
            row["cart_content"] = []
            row["error_types"].append("checkout without cart")

    # ATC without product
    if row.get("event_type") == "Add to Cart" and random.random() < 0.03:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["product_id"] = None
            row["error_types"].append("missing add to cart product")

    return row


def time_anomaly(row, previous_row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    if previous_row is None:
        return row

    # Timestamp anomaly
    if random.random() < 0.3:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            shift = random.choice(
                [
                    random.randint(1, 3),  # impatient
                    random.randint(30, 120),  # normal
                    random.randint(300, 1200),  # distracted - long idle
                    -random.randint(5, 300),  # goes backwards
                    random.randint(86400, 864000),  # 1-10 days gap (huge jump forward)
                ]
            )
            if previous_row.get("timestamp") is not None:
                row["timestamp"] = previous_row["timestamp"] + timedelta(seconds=shift)
                row["error_types"].append("timestamp gap anomaly")

    elif random.random() < 0.02:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            # Future timestamp
            row["timestamp"] = fake.future_datetime(end_date="+10y")
            row["error_types"].append("future timestamp")

    return row


def break_cart_persistence(row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    # Cart content corruption
    cart = row.get("cart_content")

    if isinstance(cart, str):
        try:
            cart = ast.literal_eval(cart)
        except Exception:
            cart = []

    if cart is None:
        cart = []

    r = random.random()

    if r < 0.3:
        if len(cart) > 0 and len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            cart = random.sample(cart, k=max(0, len(cart) // 2))
            row["cart_content"] = cart
            row["cart_size"] = len(cart)
            row["error_types"].append("partial cart loss")

    elif r < 0.9:
        if len(cart) > 0 and len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["cart_content"] = []
            row["cart_size"] = 0
            row["error_types"].append("cart reset")

    elif r < 0.95:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["cart_content"] = None
            row["cart_size"] = None
            row["error_types"].append("cart is none")

    else:
        if len(cart) > 0 and len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            random_product = random.choice(cart)
            exploded_cart = cart + [random_product] * random.randint(10, 30)
            row["cart_content"] = exploded_cart
            row["cart_size"] = len(exploded_cart)
            row["error_types"].append("cart explosion")

    return row


def messy_search_term(row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    # Malformed search term (10% of search events)
    if row.get("event_type") != "Search View":
        return row

    original_term = row.get("search_term") or fake.word()

    ops = [
        lambda t: t + random.choice(["!", "??", "."]),
        lambda t: t.replace("a", "aa"),
        lambda t: t[:-1] if len(t) > 1 else t,  # Truncate
        lambda t: "".join(random.sample(t, len(t))) if len(t) > 2 else t,  # Shuffle
        lambda t: " " * random.randint(1, 5),
        lambda t: "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 10))
        ),
    ]

    if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
        search_term = random.choice(ops)(original_term)
        row["page"] = f"/search?q={search_term}"
        row["error_types"].append("messy search term")

    return row


def wrong_event_sequence(previous_row, row, session_rows):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return row

    if random.random() < 0.05:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            row["event_type"] = random.choice(
                [
                    "Payment Attempt",
                    "Checkout Start",
                    "Add to Cart",
                    "Cart View",
                    "Home View",
                ]
            )
            row["error_types"].append("impossible event sequence")

    # --- Event Repeat ---
    if previous_row is not None and random.random() < 0.05:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            new_row = clone_clean_row(previous_row)
            new_row["timestamp"] = row["timestamp"] + timedelta(
                seconds=random.randint(1, 10)
            )
            new_row["event_order"] = row["event_order"]
            new_row["clickstream_id"] = f"{row['session_id']}_{row['event_order']}"
            new_row["error_types"] = ["event repeat"]

            return new_row

    # --- Random backtracking ---
    if len(session_rows) > 0 and random.random() < 0.05:
        if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
            old = random.choice(session_rows)
            new_row = clone_clean_row(row)
            new_row["page"] = old.get("page")
            new_row["product_id"] = old.get("product_id")
            new_row["product_name"] = old.get("product_name")
            new_row["category"] = old.get("category")
            new_row["error_types"] = ["random backtracking"]

            return new_row

    # --- Revisit previous product view
    if random.random() < 0.08:
        product_views = [
            r for r in session_rows if r.get("event_type") == "Product View"
        ]

        if len(product_views) > 0:
            old = random.choice(product_views)
            new_row = clone_clean_row(row)
            new_row["page"] = old.get("page")
            new_row["product_id"] = old.get("product_id")
            new_row["product_name"] = old.get("product_name")
            new_row["category"] = old.get("category")
            new_row["error_types"] = ["replay event"]

            return new_row

    return row


def duplicate_event(row):
    if len(set(row["error_types"])) < MAX_ERRORS_PER_ROW:
        # Duplicate event
        if row.get("timestamp") is not None:
            duplicate_row = clone_clean_row(row)
            duplicate_row["timestamp"] = row["timestamp"] + timedelta(
                seconds=random.randint(1, 3)
            )
            duplicate_row["error_types"] = row["error_types"] + ["duplicate event"]

            return duplicate_row

    return None


def inject_bot_traffic(ctx, row):
    if len(set(row.get("error_types", []))) >= MAX_ERRORS_PER_ROW:
        return []

    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map

    bot_rows = []
    bot_session_id = str(uuid.uuid4())
    current_time = row.get("timestamp") or pd.Timestamp.now()
    n_events = random.randint(5, 20)

    for i in range(n_events):
        bot_row = clone_clean_row(row)
        current_time += timedelta(
            seconds=random.choice(
                [random.uniform(0.1, 0.5), random.uniform(1, 5), random.uniform(10, 60)]
            )
        )
        # --- Event details ---
        event_type = random.choices(
            [
                "Home View",
                "Search View",
                "Category View",
                "Product View",
                "Cart View",
            ],
            weights=[10, 25, 20, 40, 5],
            k=1,
        )[0]
        product_id = random.choice(product_ids)
        product_name = product_name_map.get(product_id)
        category = random.choice(CATEGORIES)
        bot_row["session_id"] = bot_session_id
        bot_row["event_order"] = i + 1
        bot_row["clickstream_id"] = f"{bot_session_id}_{i + 1}"
        bot_row["timestamp"] = current_time
        bot_row["event_type"] = event_type
        bot_row["scroll_depth"] = random.uniform(0, 20)
        bot_row["error_types"] = ["bot traffic"]

        # --- Event Specific Logic ---
        if event_type == "Home View":
            bot_row["page"] = "/"
            bot_row["product_id"] = None
            bot_row["product_name"] = None
            bot_row["category"] = None

        elif event_type == "Search View":
            search_term = get_search_term(ctx)
            bot_row["page"] = f"/search?q={search_term}"
            bot_row["product_id"] = None
            bot_row["product_name"] = None
            bot_row["category"] = None

        elif event_type == "Category View":
            bot_row["page"] = f"/category/{category}"
            bot_row["category"] = category
            bot_row["product_id"] = None
            bot_row["product_name"] = product_name

        elif event_type == "Product View":
            bot_row["page"] = f"/product/{product_id}"
            bot_row["product_id"] = product_id
            bot_row["category"] = category

        elif event_type == "Cart View":
            bot_row["page"] = "/cart"
            bot_row["scroll_depth"] = None

        bot_rows.append(bot_row)

    return bot_rows


def orphan_sessions(ctx):
    """
    Generates sessions where the session_id has no Home View / landing event —
    as if the tracker missed session start. Every event in the session references
    a valid customer_id but the session itself is unresolvable to a first touch,
    making attribution and funnel analysis break downstream.
    """
    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map
    customer_ids = ctx.customers.customer_ids

    orphan_rows = []
    # Generate a small handful of orphan sessions
    n_orphan_sessions = random.randint(5, 20)

    for _ in range(n_orphan_sessions):
        orphan_session_id = str(uuid.uuid4())
        # Attach to a real customer so FK constraints look fine but session is untraceable
        customer_id = random.choice(customer_ids)
        current_time = fake.date_time_between(start_date="-2y", end_date="now")
        n_events = random.randint(3, 12)

        # Orphan sessions skip the landing event — start mid-funnel
        mid_funnel_events = [
            "Product View",
            "Add to Cart",
            "Cart View",
            "Search View",
            "Category View",
            "Checkout Start",
            "Payment Attempt",
        ]

        cart_content = []

        for i in range(n_events):
            event_type = random.choice(mid_funnel_events)
            product_id = None
            product_name = None
            category = None
            page = None
            scroll_depth = random.uniform(0, 100)

            if event_type == "Product View":
                product_id = random.choice(product_ids)
                product_name = product_name_map.get(product_id)
                category = product_category_map.get(product_id)
                page = f"/product/{product_id}"

            elif event_type == "Add to Cart":
                product_id = random.choice(product_ids)
                product_name = product_name_map.get(product_id)
                category = product_category_map.get(product_id)
                page = f"/product/{product_id}"
                cart_content.append(product_id)

            elif event_type == "Cart View":
                page = "/cart"
                scroll_depth = None

            elif event_type == "Search View":
                term = get_search_term(ctx)
                page = f"/search?q={term}"

            elif event_type == "Category View":
                category = random.choice(CATEGORIES)
                page = f"/category/{category}"

            elif event_type in ("Checkout Start", "Payment Attempt"):
                page = "/checkout"
                if not cart_content:
                    # Orphan checkout with nothing in cart — extra dirty
                    cart_content = []

            current_time += timedelta(seconds=random.randint(10, 300))

            orphan_rows.append(
                {
                    "clickstream_id": f"{orphan_session_id}_{i + 1}",
                    "session_id": orphan_session_id,
                    "customer_id": customer_id,
                    "customer_segment": None,  # Unknown — session never resolved
                    "campaign_ids": [],
                    "has_treatment_campaign": None,
                    "has_control_campaign": None,
                    "device_category": random.choice(["Desktop", "Mobile", "Tablet"]),
                    "referrer": None,  # No referrer — orphaned
                    "location": None,
                    "timestamp": current_time,
                    "event_order": i
                    + 1,  # Starts at 1 but there's no event_order = 0 landing
                    "event_type": event_type,
                    "page": page,
                    "scroll_depth": scroll_depth,
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "promotion_id": None,
                    "bundle_id": None,
                    "bounce_flag": 0,
                    "cart_size": len(cart_content),
                    "cart_content": cart_content.copy(),
                    "purchased_items": [],
                    "stock_status": None,
                    "error_types": ["orphan session"],
                }
            )

    return orphan_rows
