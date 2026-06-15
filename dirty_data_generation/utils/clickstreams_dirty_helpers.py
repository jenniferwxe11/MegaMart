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

# ---------------------------------------------------------------------------
# Core error management helpers
# ---------------------------------------------------------------------------


def coinflip(prob: float) -> bool:
    return random.random() < prob


def _get_errors(df: pd.DataFrame, idx) -> list:
    """Safely retrieve error list for a row."""
    errors = df.at[idx, "error_types"]
    if isinstance(errors, list):
        return errors.copy()
    return []


def _set_errors(df: pd.DataFrame, idx, errors: list) -> None:
    """Safely write error list back."""
    df.at[idx, "error_types"] = errors


def _under_cap(errors: list, max_errors: int = MAX_ERRORS_PER_ROW) -> bool:
    """Check whether a row can receive more errors."""
    return len(set(errors)) < max_errors


def append_error(
    df: pd.DataFrame,
    indices,
    error_label: str,
    max_errors: int = MAX_ERRORS_PER_ROW,
) -> None:
    """
    Append an error label to rows by index.
    Deduplicates labels and respects error cap.
    """
    for idx in list(indices):
        errors = _get_errors(df, idx)
        if not _under_cap(errors, max_errors):
            continue
        if error_label not in errors:
            errors.append(error_label)
        _set_errors(df, idx, errors)


# ---------------------------------------------------------------------------
# Row level helpers
# ---------------------------------------------------------------------------


def _row_get_errors(row: dict) -> list:
    errors = row.get("error_types", [])
    return errors if isinstance(errors, list) else []


def _row_can_add(row: dict) -> bool:
    return _under_cap(_row_get_errors(row))


def _row_add_error(row: dict, label: str) -> bool:
    """
    Add *label* to row["error_types"] if under cap and not already present.
    Returns True if the label was added.
    """
    errors = _row_get_errors(row)
    if not _under_cap(errors):
        return False
    if label not in errors:
        errors.append(label)
        row["error_types"] = errors
        return True
    return False


# ---------------------------------------------------------------------------
# Session/corruption budget helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Corruption functions
# ---------------------------------------------------------------------------


def missing_fields(row):
    if not _row_can_add(row):
        return row

    field = random.choice(
        [
            "product_id",
            "category",
            "scroll_depth",
            "location",
            "cart_content",
            "cart_size",
            "event_timestamp",
            "event_order",
            "event_type",
            "page",
            "device_category",
        ]
    )

    row[field] = None
    _row_add_error(row, f"missing {field}")
    return row


def populate_wrong_fields(ctx, row):
    product_ids = ctx.products.product_ids

    if row.get("scroll_depth") is None:
        if _row_add_error(row, "populate scroll depth"):
            row["scroll_depth"] = random.randint(0, 100)

    if row.get("category") is None:
        if _row_add_error(row, "populate category"):
            row["category"] = random.choices(
                list(CATEGORY_PRODUCT_DISTRIBUTION.keys()),
                weights=list(CATEGORY_PRODUCT_DISTRIBUTION.values()),
                k=1,
            )[0]

    if row.get("product_id") is None:
        if _row_add_error(row, "populate product id"):
            row["product_id"] = random.choice(product_ids)

    if row.get("cart_size") is None:
        if _row_add_error(row, "populate cart size"):
            row["cart_size"] = random.randint(0, 20)

    return row


def mismatch_fields(ctx, row):
    product_ids = ctx.products.product_ids

    if coinflip(0.3) and row.get("event_type") in (
        "Product View",
        "Add to Cart",
        "Remove from Cart",
    ):
        if _row_add_error(row, "mismatch product"):
            row["product_id"] = random.choice(product_ids)

    if coinflip(0.3) and row.get("cart_size") is not None:
        if _row_add_error(row, "mismatch cart size"):
            row["cart_size"] = random.randint(0, 20)

    if coinflip(0.2) and row.get("scroll_depth") is not None:
        if _row_add_error(row, "mismatch scroll depth"):
            row["scroll_depth"] += random.uniform(-25, 25)

    return row


def field_corruption(row):
    if row.get("scroll_depth") is not None and coinflip(0.2):
        if _row_add_error(row, "scroll out of bound"):
            row["scroll_depth"] = random.choice(
                [random.uniform(100.1, 150), random.uniform(-20, -0.1)]
            )

    if row.get("category") is not None and coinflip(0.3):
        if _row_add_error(row, "category corruption"):
            row["category"] = fake.word()

    if row.get("bounce_flag") is not None and coinflip(0.2):
        if _row_add_error(row, "bounce flag corruption"):
            row["bounce_flag"] = "Bounced"

    if row.get("event_type") == "Checkout Start" and coinflip(0.3):
        if _row_add_error(row, "checkout without cart"):
            row["cart_size"] = 0
            row["cart_content"] = []

    if row.get("event_type") == "Add to Cart" and coinflip(0.03):
        if _row_add_error(row, "missing add to cart product"):
            row["product_id"] = None

    return row


def time_anomaly(row, previous_row):
    if not _row_can_add(row) or previous_row is None:
        return row

    if coinflip(0.3):
        if _row_add_error(row, "timestamp gap anomaly"):
            shift = random.choice(
                [
                    random.randint(1, 3),
                    random.randint(30, 120),
                    random.randint(300, 1200),
                    -random.randint(5, 300),
                    random.randint(86400, 864000),
                ]
            )
            if previous_row.get("event_timestamp") is not None:
                row["event_timestamp"] = previous_row["event_timestamp"] + timedelta(
                    seconds=shift
                )

    elif coinflip(0.02):
        if _row_add_error(row, "future timestamp"):
            row["event_timestamp"] = fake.future_datetime(end_date="+10y")

    return row


def break_cart_persistence(row):
    if not _row_can_add(row):
        return row

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
        if len(cart) > 0 and _row_add_error(row, "partial cart loss"):
            cart = random.sample(cart, k=max(0, len(cart) // 2))
            row["cart_content"] = cart
            row["cart_size"] = len(cart)

    elif r < 0.9:
        if len(cart) > 0 and _row_add_error(row, "cart reset"):
            row["cart_content"] = []
            row["cart_size"] = 0

    elif r < 0.95:
        if _row_add_error(row, "cart is none"):
            row["cart_content"] = None
            row["cart_size"] = None

    else:
        if len(cart) > 0 and _row_add_error(row, "cart explosion"):
            random_product = random.choice(cart)
            exploded_cart = cart + [random_product] * random.randint(10, 30)
            row["cart_content"] = exploded_cart
            row["cart_size"] = len(exploded_cart)

    return row


def messy_search_term(row):
    if not _row_can_add(row) or row.get("event_type") != "Search View":
        return row

    original_term = row.get("search_term") or fake.word()

    ops = [
        lambda t: t + random.choice(["!", "??", "."]),
        lambda t: t.replace("a", "aa"),
        lambda t: t[:-1] if len(t) > 1 else t,
        lambda t: "".join(random.sample(t, len(t))) if len(t) > 2 else t,
        lambda t: " " * random.randint(1, 5),
        lambda t: "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 10))
        ),
    ]

    if _row_add_error(row, "messy search term"):
        search_term = random.choice(ops)(original_term)
        row["page"] = f"/search?q={search_term}"

    return row


def wrong_event_sequence(previous_row, row, session_rows):
    if not _row_can_add(row):
        return row

    if coinflip(0.05):
        if _row_add_error(row, "impossible event sequence"):
            row["event_type"] = random.choice(
                [
                    "Payment Attempt",
                    "Checkout Start",
                    "Add to Cart",
                    "Cart View",
                    "Home View",
                ]
            )

    # --- Event Repeat ---
    if previous_row is not None and coinflip(0.05):
        new_row = clone_clean_row(previous_row)
        if (
            row.get("event_timestamp") is not None
            and new_row.get("event_timestamp") is not None
        ):
            new_row["event_timestamp"] = row["event_timestamp"] + timedelta(
                seconds=random.randint(1, 10)
            )
            new_row["event_order"] = row["event_order"]
            new_row["clickstream_id"] = f"{row['session_id']}_{row['event_order']}"
            new_row["error_types"] = ["event repeat"]
            return new_row

    # --- Random backtracking ---
    if len(session_rows) > 0 and coinflip(0.05):
        old = random.choice(session_rows)
        new_row = clone_clean_row(row)
        new_row["page"] = old.get("page")
        new_row["product_id"] = old.get("product_id")
        new_row["product_name"] = old.get("product_name")
        new_row["category"] = old.get("category")
        new_row["error_types"] = ["random backtracking"]
        return new_row

    # --- Revisit previous product view ---
    if coinflip(0.08):
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
    if _row_can_add(row):
        if row.get("event_timestamp") is not None:
            duplicate_row = clone_clean_row(row)
            duplicate_row["event_timestamp"] = row["event_timestamp"] + timedelta(
                seconds=random.randint(1, 3)
            )
            duplicate_row["error_types"] = _row_get_errors(row) + ["duplicate event"]
            return duplicate_row
    return None


def inject_bot_traffic(ctx, row):
    if not _row_can_add(row):
        return []

    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map

    bot_rows = []
    bot_session_id = str(uuid.uuid4())
    current_time = row.get("event_timestamp") or pd.Timestamp.now()
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
            ["Home View", "Search View", "Category View", "Product View", "Cart View"],
            weights=[10, 25, 20, 40, 5],
            k=1,
        )[0]
        product_id = random.choice(product_ids)
        product_name = product_name_map.get(product_id)
        category = random.choice(CATEGORIES)

        bot_row["session_id"] = bot_session_id
        bot_row["event_order"] = i + 1
        bot_row["clickstream_id"] = f"{bot_session_id}_{i + 1}"
        bot_row["event_timestamp"] = current_time
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
    n_orphan_sessions = random.randint(5, 20)

    for _ in range(n_orphan_sessions):
        orphan_session_id = str(uuid.uuid4())
        customer_id = random.choice(customer_ids)
        current_time = fake.date_time_between(start_date="-2y", end_date="now")
        n_events = random.randint(3, 12)

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
                    cart_content = []

            current_time += timedelta(seconds=random.randint(10, 300))

            orphan_rows.append(
                {
                    "clickstream_id": f"{orphan_session_id}_{i + 1}",
                    "session_id": orphan_session_id,
                    "customer_id": customer_id,
                    "customer_segment": None,
                    "campaign_ids": [],
                    "has_treatment_campaign": False,
                    "has_control_campaign": False,
                    "device_category": random.choice(["Desktop", "Mobile", "Tablet"]),
                    "referrer": None,
                    "location": None,
                    "event_timestamp": current_time,
                    "event_order": i + 1,
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
