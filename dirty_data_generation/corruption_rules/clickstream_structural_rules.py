# dirty_data_generation/corruption_rules/clickstream_structural_rules.py

import random
import uuid
from datetime import timedelta

from faker import Faker

from data_generation.config.products_config import CATEGORIES

fake = Faker()


# ---------------------------------------------------------------------------
# Orphan / Invalid Landing Sessions
# ---------------------------------------------------------------------------


def inject_orphan_sessions(
    ctx,
    source_df,
    n_sessions: int | None = None,
):
    """
    Creates sessions whose first event is not a valid landing event.

    This is a structural corruption rather than a row-level corruption.

    Intended to violate:
        first_event_matches_landing_behaviour
        invalid_first_event
    """

    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map
    customer_ids = ctx.customers.customer_ids

    # Nothing to inject if the required source data is unavailable.
    if source_df.empty or not product_ids or not customer_ids:
        return []

    if n_sessions is None:
        n_sessions = random.randint(5, 20)

    orphan_rows = []

    # Deliberately invalid first event types.
    invalid_first_event_types = [
        "Product View",
        "Add to Cart",
        "Cart View",
        "Checkout Start",
        "Payment Attempt",
    ]

    # Valid events that can follow the first event.
    subsequent_event_types = [
        "Home View",
        "Search View",
        "Category View",
        "Product View",
        "Add to Cart",
        "Cart View",
        "Checkout Start",
        "Payment Attempt",
    ]

    for _ in range(n_sessions):

        source_row = source_df.sample(1).iloc[0]

        customer_id = source_row["customer_id"]
        customer_segment = source_row["customer_segment"]
        device_category = source_row["device_category"]
        referrer = source_row["referrer"]
        location = source_row["location"]

        session_id = str(uuid.uuid4())

        current_time = fake.date_time_between(
            start_date="-2y",
            end_date="now",
        )

        n_events = random.randint(3, 12)

        # ---------------------------------------------------------------
        # Ensure the FIRST event is deliberately invalid.
        # ---------------------------------------------------------------

        event_types = [random.choice(invalid_first_event_types)]

        event_types.extend(
            random.choice(subsequent_event_types) for _ in range(n_events - 1)
        )

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

            # -----------------------------------------------------------
            # Event-specific construction
            # -----------------------------------------------------------

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

            # -----------------------------------------------------------
            # Timestamp
            # -----------------------------------------------------------

            current_time += timedelta(seconds=random.randint(10, 300))

            # -----------------------------------------------------------
            # Build row
            # -----------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Bot Traffic
# ---------------------------------------------------------------------------


def inject_bot_traffic(
    ctx,
    row,
    n_events: int | None = None,
):
    """
    Generates a synthetic bot session.

    This is intentionally structural and should not be mixed with
    ordinary row-level corruption.

    NOTE:
        There is currently no dbt test specifically validating bot traffic.
        Keep this injector unused unless bot traffic is an explicit
        dirty-data requirement.
    """

    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map

    if not product_ids:
        return []

    if n_events is None:
        n_events = random.randint(5, 20)

    bot_session_id = str(uuid.uuid4())

    # Use the supplied row only as a template.
    source_row = row.copy()

    current_time = source_row.get("event_timestamp") or fake.date_time_between(
        start_date="-30d",
        end_date="now",
    )

    bot_rows = []

    event_types = [
        "Home View",
        "Search View",
        "Category View",
        "Product View",
        "Cart View",
    ]

    for event_order in range(1, n_events + 1):

        # ---------------------------------------------------------------
        # Create a NEW dictionary for every event.
        # ---------------------------------------------------------------

        bot_row = source_row.copy()

        event_type = random.choice(event_types)

        current_time += timedelta(
            seconds=random.choice(
                [
                    random.uniform(0.1, 0.5),
                    random.uniform(1, 5),
                    random.uniform(10, 60),
                ]
            )
        )

        bot_row["session_id"] = bot_session_id

        bot_row["event_order"] = event_order

        bot_row["clickstream_id"] = f"{bot_session_id}_{event_order}"

        bot_row["event_timestamp"] = current_time

        bot_row["event_type"] = event_type

        bot_row["bounce_flag"] = 0

        # Reset event-specific fields.
        bot_row["product_id"] = None
        bot_row["product_name"] = None
        bot_row["category"] = None
        bot_row["promotion_ids"] = []
        bot_row["bundle_ids"] = []
        bot_row["cart_content"] = []
        bot_row["cart_size"] = 0
        bot_row["purchased_items"] = []
        bot_row["stock_status"] = None

        # ---------------------------------------------------------------
        # Event-specific fields
        # ---------------------------------------------------------------

        if event_type == "Home View":

            bot_row["page"] = "/home"
            bot_row["scroll_depth"] = random.uniform(0, 20)

        elif event_type == "Search View":

            bot_row["page"] = "/search?q=bot"
            bot_row["scroll_depth"] = random.uniform(0, 20)

        elif event_type == "Category View":

            category = random.choice(CATEGORIES)

            bot_row["category"] = category
            bot_row["page"] = f"/category/{category}"
            bot_row["scroll_depth"] = random.uniform(0, 20)

        elif event_type == "Product View":

            product_id = random.choice(product_ids)

            bot_row["product_id"] = product_id
            bot_row["product_name"] = product_name_map.get(product_id)
            bot_row["page"] = f"/product/{product_id}"
            bot_row["scroll_depth"] = random.uniform(0, 20)

        elif event_type == "Cart View":

            bot_row["page"] = "/cart"
            bot_row["scroll_depth"] = None

        bot_rows.append(bot_row)

    return bot_rows


# ---------------------------------------------------------------------------
# Structural Corruption Registry
# ---------------------------------------------------------------------------


CLICKSTREAM_STRUCTURAL_RULES = [
    inject_orphan_sessions,
]
