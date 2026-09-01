# dirty_data_generation/corruption_rules/clickstream_structural_rules.py

import random
import uuid
from datetime import timedelta

from faker import Faker

from data_generation.config.clickstreams_config import (
    LANDING_PAGE_BEHAVIOUR,
    VALID_EVENT_TRANSITIONS,
)
from data_generation.config.constants import (
    DATA_END_DATE,
    DATA_START_DATE,
)
from data_generation.config.products_config import CATEGORIES

fake = Faker()

# =============================================================================
# Config derived Event Types
# =============================================================================


ALL_EVENT_TYPES = sorted(
    set(VALID_EVENT_TRANSITIONS)
    | {
        next_event
        for transitions in VALID_EVENT_TRANSITIONS.values()
        for next_event in transitions
    }
)


def _choose_invalid_first_event(referrer: str) -> str | None:
    """
    Choose an event that is invalid as the first event for the given referrer.
    """

    valid_first_events = set(LANDING_PAGE_BEHAVIOUR.get(referrer, {}))

    invalid_events = [
        event_type
        for event_type in ALL_EVENT_TYPES
        if event_type not in valid_first_events
    ]

    if not invalid_events:
        return None

    return random.choice(invalid_events)


def _choose_next_event(previous_event: str) -> str | None:
    """
    Choose the next event according to VALID_EVENT_TRANSITIONS.

    This keeps the non corrupted portion of the generated session
    behaviourally valid.
    """

    transitions = VALID_EVENT_TRANSITIONS.get(previous_event)

    if not transitions:
        return None

    events = list(transitions.keys())
    probabilities = list(transitions.values())

    return random.choices(
        events,
        weights=probabilities,
        k=1,
    )[0]


# =============================================================================
# Orphan / Invalid Landing Sessions
# =============================================================================


def inject_orphan_sessions(
    ctx,
    source_df,
    n_sessions: int | None = None,
):
    """
    Creates sessions whose first event is not a valid landing event.

    This is a structural corruption rather than a row level corruption.

    Violates:
        first_event_matches_landing_behaviour
        invalid_first_event
    """

    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map
    customer_ids = ctx.customers.customer_ids

    if source_df.empty or not product_ids or not customer_ids:
        return []

    if n_sessions is None:
        n_sessions = random.randint(5, 20)

    orphan_rows = []

    for _ in range(n_sessions):

        # ---------------------------------------------------------------------
        # Select a source session/customer context
        # ---------------------------------------------------------------------

        source_row = source_df.sample(1).iloc[0]

        customer_id = source_row["customer_id"]
        customer_segment = source_row["customer_segment"]
        device_category = source_row["device_category"]
        referrer = source_row["referrer"]
        location = source_row["location"]

        session_id = str(uuid.uuid4())

        current_time = fake.date_time_between(
            start_date=DATA_START_DATE,
            end_date=DATA_END_DATE,
        )

        n_events = random.randint(3, 12)

        # ---------------------------------------------------------------------
        # First Event
        # ---------------------------------------------------------------------

        first_event = _choose_invalid_first_event(referrer)

        if first_event is None:
            continue

        event_types = [first_event]

        # ---------------------------------------------------------------------
        # Subsequent Events
        # ---------------------------------------------------------------------

        previous_event = first_event

        for _ in range(n_events - 1):

            next_event = _choose_next_event(previous_event)

            if next_event is None:
                break

            event_types.append(next_event)
            previous_event = next_event

        # ---------------------------------------------------------------------
        # Build session
        # ---------------------------------------------------------------------

        cart_content = []

        for event_order, event_type in enumerate(
            event_types,
            start=1,
        ):

            product_id = None
            product_name = None
            category = None
            page = None
            scroll_depth: float | None = random.uniform(0, 100)

            # -----------------------------------------------------------------
            # Event specific construction
            # -----------------------------------------------------------------

            if event_type == "Home View":

                page = "/home"

            elif event_type == "Product View":

                product_id = random.choice(product_ids)

                product_name = product_name_map.get(product_id)

                category = product_category_map.get(product_id)

                page = f"/product/{product_id}"

            elif event_type == "Add to Cart":

                product_id = random.choice(product_ids)

                product_name = product_name_map.get(product_id)

                category = product_category_map.get(product_id)

                page = f"/add_to_cart/{product_id}"

                cart_content.append(product_id)

            elif event_type == "Cart View":

                page = "/cart"
                scroll_depth = None

            elif event_type == "Search View":

                page = "/search?q=orphan"

            elif event_type == "Category View":

                category = random.choice(CATEGORIES)

                page = f"/category/{category}"

            elif event_type == "Checkout Start":

                page = "/checkout"

            elif event_type == "Payment Attempt":

                page = "/payment"

            elif event_type == "Remove from Cart":

                product_id = random.choice(product_ids)

                product_name = product_name_map.get(product_id)

                category = product_category_map.get(product_id)

                page = f"/remove_from_cart/{product_id}"

                if cart_content:
                    product_to_remove = random.choice(cart_content)

                    cart_content.remove(product_to_remove)

            elif event_type == "Payment Successful":

                page = "/payment/success"

                cart_content = []

            elif event_type == "Payment Failed":

                page = "/payment/fail"

            # -----------------------------------------------------------------
            # Timestamp
            # -----------------------------------------------------------------

            current_time += timedelta(seconds=random.randint(10, 300))

            # -----------------------------------------------------------------
            # Build row
            # -----------------------------------------------------------------

            row = {
                "clickstream_id": f"{session_id}_{event_order}",
                "session_id": session_id,
                "customer_id": customer_id,
                "customer_segment": customer_segment,
                "campaign_ids": [],
                "has_treatment_campaign": False,
                "has_control_campaign": False,
                "device_category": device_category,
                "referrer": referrer,
                "location": location,
                "event_timestamp": current_time,
                "event_order": event_order,
                "event_type": event_type,
                "page": page,
                "scroll_depth": scroll_depth,
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "promotion_ids": [],
                "bundle_ids": [],
                "bounce_flag": 0,
                "cart_size": len(cart_content),
                "cart_content": cart_content.copy(),
                "purchased_items": [],
                "stock_status": None,
            }

            orphan_rows.append(row)

    return orphan_rows


# =============================================================================
# Structural Corruption Registry
# =============================================================================


CLICKSTREAM_STRUCTURAL_RULES = [
    inject_orphan_sessions,
]
