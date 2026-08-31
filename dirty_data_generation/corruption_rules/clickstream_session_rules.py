# dirty_data_generation/corruption_rules/clickstream_session_rules.py

import random
from datetime import timedelta

import pandas as pd

from dirty_data_generation.config.constants import (
    MAX_ERRORS_PER_ROW,
)

# =============================================================================
# Error Helpers
# =============================================================================


def _can_add_error(df, idx) -> bool:
    """
    Check whether another corruption can be applied to this row.
    """

    value = df.at[idx, "error_count"]

    if pd.isna(value):
        return True

    return int(value) < MAX_ERRORS_PER_ROW


def _add_error(df, idx) -> bool:
    """
    Increment error_count by one.
    """

    if not _can_add_error(df, idx):
        return False

    current = df.at[idx, "error_count"]

    if pd.isna(current):
        current = 0

    df.at[idx, "error_count"] = int(current) + 1

    return True


# =============================================================================
# Session Helpers
# =============================================================================


def _session_rows(df, session_id):
    """
    Return all rows belonging to a session in event order.
    """

    return df[df["session_id"] == session_id].sort_values(
        ["event_order", "event_timestamp"],
        na_position="last",
    )


def _previous_row(df, idx):
    """
    Return the previous event in the same session based on event_order.
    """

    session_id = df.at[idx, "session_id"]
    event_order = df.at[idx, "event_order"]

    if pd.isna(session_id) or pd.isna(event_order):
        return None

    previous_rows = df[
        (df["session_id"] == session_id)
        & (df.index != idx)
        & df["event_order"].notna()
        & (df["event_order"] < event_order)
    ].sort_values("event_order")

    if previous_rows.empty:
        return None

    return previous_rows.iloc[-1]


# =============================================================================
# Event Order
# =============================================================================


def duplicate_event_order_within_session(df, idx, ctx=None):
    """
    Makes the current event share event_order with another event
    in the same session.

    Violates:
        unique_event_order_within_session
    """

    session_id = df.at[idx, "session_id"]

    if pd.isna(session_id):
        return

    if not _can_add_error(df, idx):
        return

    session_df = _session_rows(df, session_id)

    candidates = session_df[session_df.index != idx]

    if candidates.empty:
        return

    target_idx = random.choice(candidates.index.tolist())

    target_order = df.at[target_idx, "event_order"]

    if pd.isna(target_order):
        return

    if _add_error(df, idx):
        df.at[idx, "event_order"] = target_order


def non_sequential_event_order(df, idx, ctx=None):
    """
    Creates a deliberate gap in event_order.

    Example:

        1, 2, 3, 4

    becomes:

        1, 2, 7, 4

    Violates:
        sequential_event_order
    """

    session_id = df.at[idx, "session_id"]
    event_order = df.at[idx, "event_order"]

    if pd.isna(session_id) or pd.isna(event_order):
        return

    if event_order == 1:
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_order = previous_row["event_order"]

    if pd.isna(previous_order):
        return

    new_order = int(previous_order) + random.choice([2, 3, 5, 10])

    existing_orders = set(
        df.loc[
            (df["session_id"] == session_id) & (df.index != idx),
            "event_order",
        ]
        .dropna()
        .tolist()
    )

    while new_order in existing_orders:
        new_order += random.randint(2, 5)

    if _add_error(df, idx):
        df.at[idx, "event_order"] = new_order


# =============================================================================
# Timestamp
# =============================================================================


def timestamp_out_of_order(df, idx, ctx=None):
    """
    Makes the current timestamp earlier than the previous event.

    Violates:
        sequential_event_timestamp
    """

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_timestamp = previous_row["event_timestamp"]

    if pd.isna(previous_timestamp):
        return

    if _add_error(df, idx):
        df.at[idx, "event_timestamp"] = pd.Timestamp(previous_timestamp) - timedelta(
            seconds=random.randint(1, 300)
        )


def future_event_timestamp(df, idx, ctx=None):
    """
    Moves an event timestamp into the future.
    """

    value = df.at[idx, "event_timestamp"]

    if pd.isna(value):
        return

    if _add_error(df, idx):
        df.at[idx, "event_timestamp"] = pd.Timestamp.now() + timedelta(
            days=random.randint(1, 30)
        )


# =============================================================================
# Bounce Behaviour
# =============================================================================


def bounce_session_multiple_events(df, idx, ctx=None):
    """
    Marks a multi-event session as bounced.

    A bounce session should contain exactly one event.

    Violates:
        bounce_sessions_contain_exactly_one_event
    """

    session_id = df.at[idx, "session_id"]

    if pd.isna(session_id):
        return

    session_df = _session_rows(df, session_id)

    if len(session_df) < 2:
        return

    first_idx = session_df.index[0]

    if _add_error(df, first_idx):
        df.at[first_idx, "bounce_flag"] = 1


def bounce_flag_on_non_first_event(df, idx, ctx=None):
    """
    Sets bounce_flag = 1 on an event that is not the first event.

    Violates:
        bounce_flag_only_on_first_event
    """

    event_order = df.at[idx, "event_order"]

    if pd.isna(event_order):
        return

    if event_order == 1:
        return

    if _add_error(df, idx):
        df.at[idx, "bounce_flag"] = 1


# =============================================================================
# Landing / Referrer
# =============================================================================


ALLOWED_FIRST_EVENTS = {
    "organic_search": {
        "Home View",
        "Search View",
        "Product View",
    },
    "direct": {
        "Home View",
        "Category View",
        "Product View",
    },
    "social_media": {
        "Home View",
        "Product View",
        "Category View",
    },
    "email": {
        "Home View",
        "Product View",
        "Category View",
    },
    "unknown": {
        "Home View",
        "Product View",
        "Category View",
        "Search View",
    },
}


def invalid_first_event_for_referrer(df, idx, ctx=None):
    """
    Changes the first event to one that is invalid for its referrer.
    """

    event_order = df.at[idx, "event_order"]
    referrer = df.at[idx, "referrer"]

    if pd.isna(event_order):
        return

    if event_order != 1:
        return

    if referrer not in ALLOWED_FIRST_EVENTS:
        return

    allowed = ALLOWED_FIRST_EVENTS[referrer]

    all_events = {
        "Home View",
        "Category View",
        "Search View",
        "Product View",
        "Cart View",
        "Add to Cart",
        "Remove from Cart",
        "Checkout Start",
        "Payment Attempt",
        "Payment Successful",
        "Payment Failed",
    }

    invalid_events = [event for event in all_events if event not in allowed]

    if not invalid_events:
        return

    if _add_error(df, idx):
        df.at[idx, "event_type"] = random.choice(invalid_events)


# =============================================================================
# Event Transitions
# =============================================================================


VALID_TRANSITIONS = {
    "Home View": {
        "Category View",
        "Search View",
        "Product View",
    },
    "Category View": {
        "Category View",
        "Search View",
        "Product View",
        "Home View",
    },
    "Search View": {
        "Search View",
        "Category View",
        "Product View",
        "Home View",
    },
    "Product View": {
        "Product View",
        "Add to Cart",
        "Remove from Cart",
        "Category View",
        "Search View",
        "Cart View",
    },
    "Add to Cart": {
        "Product View",
        "Add to Cart",
        "Remove from Cart",
        "Cart View",
        "Checkout Start",
    },
    "Remove from Cart": {
        "Product View",
        "Add to Cart",
        "Remove from Cart",
        "Cart View",
        "Checkout Start",
    },
    "Cart View": {
        "Product View",
        "Add to Cart",
        "Remove from Cart",
        "Checkout Start",
        "Category View",
        "Search View",
    },
    "Checkout Start": {
        "Payment Attempt",
        "Cart View",
    },
    "Payment Attempt": {
        "Payment Successful",
        "Payment Failed",
    },
    "Payment Successful": {
        "Home View",
        "Category View",
        "Search View",
        "Product View",
    },
    "Payment Failed": {
        "Payment Attempt",
        "Checkout Start",
        "Cart View",
    },
}


ALL_EVENT_TYPES = list(VALID_TRANSITIONS.keys())


def invalid_event_transition(df, idx, ctx=None):
    """
    Changes the current event_type to one that is invalid
    after the previous event.
    """

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_event = previous_row["event_type"]

    valid_next_events = VALID_TRANSITIONS.get(
        previous_event,
        set(),
    )

    invalid_events = [
        event for event in ALL_EVENT_TYPES if event not in valid_next_events
    ]

    if not invalid_events:
        return

    current_event = df.at[idx, "event_type"]

    candidates = [event for event in invalid_events if event != current_event]

    if not candidates:
        return

    if _add_error(df, idx):
        df.at[idx, "event_type"] = random.choice(candidates)


# =============================================================================
# Checkout Behaviour
# =============================================================================


def checkout_start_without_cart(df, idx, ctx=None):
    """
    Checkout Start requires a non-empty cart.

    Corruption:
        Clears the cart immediately before checkout.
    """

    if df.at[idx, "event_type"] != "Checkout Start":
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_cart = previous_row["cart_content"]

    if not isinstance(previous_cart, (list, tuple)):
        return

    if not previous_cart:
        return

    if _add_error(df, idx):
        df.at[idx, "cart_content"] = []
        df.at[idx, "cart_size"] = 0


# =============================================================================
# Cart Behaviour
# =============================================================================


def add_to_cart_does_not_increase_cart(
    df,
    idx,
    ctx=None,
):
    """
    Add to Cart should add product_id to the previous cart.

    Corruption:
        Keeps the cart exactly the same.
    """

    if df.at[idx, "event_type"] != "Add to Cart":
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_cart = previous_row["cart_content"]

    if not isinstance(previous_cart, (list, tuple)):
        previous_cart = []

    previous_cart = list(previous_cart)

    if _add_error(df, idx):
        df.at[idx, "cart_content"] = previous_cart.copy()
        df.at[idx, "cart_size"] = len(previous_cart)


def remove_from_cart_does_not_reduce_cart(
    df,
    idx,
    ctx=None,
):
    """
    Remove from Cart should remove product_id from the previous cart.

    Corruption:
        Keeps the cart unchanged.
    """

    if df.at[idx, "event_type"] != "Remove from Cart":
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_cart = previous_row["cart_content"]

    if not isinstance(previous_cart, (list, tuple)):
        return

    previous_cart = list(previous_cart)

    if not previous_cart:
        return

    if _add_error(df, idx):
        df.at[idx, "cart_content"] = previous_cart.copy()
        df.at[idx, "cart_size"] = len(previous_cart)


def non_cart_event_changes_cart(
    df,
    idx,
    ctx=None,
):
    """
    Non-cart events should preserve cart state.

    Corruption:
        Adds a product to the cart.
    """

    event_type = df.at[idx, "event_type"]

    if event_type not in {
        "Home View",
        "Category View",
        "Search View",
        "Product View",
        "Cart View",
        "Checkout Start",
        "Payment Attempt",
        "Payment Successful",
        "Payment Failed",
    }:
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_cart = previous_row["cart_content"]

    if not isinstance(previous_cart, (list, tuple)):
        previous_cart = []

    new_cart = list(previous_cart)

    if ctx is not None:
        product_ids = ctx.products.products_df["product_id"].dropna().tolist()
    else:
        product_ids = []

    if product_ids:
        new_cart.append(random.choice(product_ids))
    else:
        new_cart.append("__CORRUPTED_CART_PRODUCT__")

    if _add_error(df, idx):
        df.at[idx, "cart_content"] = new_cart
        df.at[idx, "cart_size"] = len(new_cart)


# =============================================================================
# Payment / Cart Behaviour
# =============================================================================


def payment_successful_cart_mismatch(
    df,
    idx,
    ctx=None,
):
    """
    Payment Successful should remove purchased items from the cart.

    Corruption:
        Leaves purchased items in the cart.
    """

    if df.at[idx, "event_type"] != "Payment Successful":
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_cart = previous_row["cart_content"]
    purchased_items = df.at[idx, "purchased_items"]

    if not isinstance(previous_cart, (list, tuple)):
        return

    if not isinstance(purchased_items, (list, tuple)):
        return

    previous_cart = list(previous_cart)
    purchased_items = list(purchased_items)

    if not purchased_items:
        return

    new_cart = previous_cart.copy()

    for product_id in purchased_items:
        if product_id not in new_cart:
            new_cart.append(product_id)

    if _add_error(df, idx):
        df.at[idx, "cart_content"] = new_cart
        df.at[idx, "cart_size"] = len(new_cart)


def payment_failed_cart_mismatch(
    df,
    idx,
    ctx=None,
):
    """
    Payment Failed should preserve the cart.

    Corruption:
        Removes an item from the cart.
    """

    if df.at[idx, "event_type"] != "Payment Failed":
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_cart = previous_row["cart_content"]

    if not isinstance(previous_cart, (list, tuple)):
        return

    previous_cart = list(previous_cart)

    if not previous_cart:
        return

    new_cart = previous_cart.copy()

    new_cart.pop(random.randrange(len(new_cart)))

    if _add_error(df, idx):
        df.at[idx, "cart_content"] = new_cart
        df.at[idx, "cart_size"] = len(new_cart)


# =============================================================================
# Purchased Items
# =============================================================================


def purchased_items_not_in_previous_cart(
    df,
    idx,
    ctx,
):
    """
    purchased_items should be a subset of the previous cart.

    Corruption:
        Adds a product that was not in the previous cart.
    """

    if df.at[idx, "event_type"] != "Payment Successful":
        return

    if not _can_add_error(df, idx):
        return

    previous_row = _previous_row(df, idx)

    if previous_row is None:
        return

    previous_cart = previous_row["cart_content"]

    if not isinstance(previous_cart, (list, tuple)):
        return

    previous_cart = set(previous_cart)

    purchased_items = df.at[idx, "purchased_items"]

    if not isinstance(purchased_items, (list, tuple)):
        purchased_items = []

    purchased_items = list(purchased_items)

    product_ids = ctx.products.products_df["product_id"].dropna().tolist()

    candidates = [
        product_id for product_id in product_ids if product_id not in previous_cart
    ]

    if not candidates:
        return

    corrupted_items = purchased_items.copy()

    corrupted_items.append(random.choice(candidates))

    if _add_error(df, idx):
        df.at[idx, "purchased_items"] = corrupted_items
