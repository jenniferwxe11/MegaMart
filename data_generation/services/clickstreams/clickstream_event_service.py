import random

import numpy as np
import pandas as pd

from data_generation.config.clickstreams_config import (
    EVENT_PAGE_MAPPING,
    IN_STOCK_STATUS,
    TIME_ON_PAGE,
)
from data_generation.config.products_config import CATEGORY_AFFINITY, CATEGORY_ITEMS
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_product_stock_status,
    get_random_in_stock_product_from_category,
    get_random_product_from_category,
    get_random_product_from_search_term,
    get_search_term,
    get_segment_category,
    slugify,
)
from data_generation.services.clickstreams.clickstream_session_service import (
    determine_purchase_alpha_beta,
    generate_scroll_depth,
)


def resolve_scroll_and_time(event_type: str, mission_choice: str) -> tuple:
    """
    Returns (scroll_depth, time_on_page) for the event.
    Browsing events get scroll depth; action events do not.
    """
    low, mode, high = TIME_ON_PAGE.get(event_type, (3, 8, 25))

    if event_type in ("Home View", "Search View", "Category View", "Product View"):
        # Scroll depth skewed to mission choice
        scroll_depth = generate_scroll_depth(mission_choice)

        # Time on page affected by scroll depth
        time_on_page = random.triangular(low, high, mode) * (
            0.8 + (scroll_depth / 100) * 0.6
        )
    else:
        # No scroll depth
        scroll_depth = None
        time_on_page = random.triangular(low, high, mode)

    return scroll_depth, time_on_page


def resolve_page(
    event_type: str,
    product_id: str | None,
    category: str | None,
    search_term: str | None,
) -> str:
    """
    Maps event type + context to a URL page string.
    """
    template = EVENT_PAGE_MAPPING.get(event_type, "")
    if not template:
        return template

    if "{product_id}" in template and product_id:
        return template.format(product_id=product_id)
    elif "{category}" in template and category:
        return template.format(category=slugify(category))
    elif "{search_term}" in template and search_term:
        return template.format(search_term=search_term)
    return template


def resolve_remove_from_cart(
    ctx,
    cart_content: list[str],
) -> tuple:
    """
    Picks a product to remove.
    Returns (product_id, category, product_name, updated_cart).
    """
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map

    product_id = random.choice(cart_content)
    category = product_category_map.get(product_id, None)
    product_name = product_name_map.get(product_id, None)
    cart_content = cart_content.copy()
    cart_content.remove(product_id)
    return product_id, category, product_name, cart_content


def resolve_add_to_cart(
    ctx,
    product_id: str | None,
    previous_product_id: str | None,
    previous_category: str,
    cart_content: list,
    store_id: str,
    timestamp,
) -> tuple:
    """
    Resolves which product gets added to cart.
    Returns (product_id, category, product_name, updated_cart).
    """
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map

    if product_id is None:
        # Add in stock product from previous product view into cart
        if previous_product_id:
            # Check if product is in stock
            stock_status = get_product_stock_status(
                ctx, store_id, previous_product_id, timestamp
            )
            if stock_status in IN_STOCK_STATUS:
                product_id = previous_product_id

        # Fallback if previous product not usable
        if product_id is None:
            product_id = get_random_in_stock_product_from_category(
                ctx, previous_category, store_id, timestamp
            )

    category = (
        product_category_map.get(product_id)
        if product_id is not None
        else previous_category
    )

    product_name = product_name_map.get(product_id, None)
    cart_content = cart_content.copy()
    cart_content.append(product_id)
    return product_id, category, product_name, cart_content


def resolve_product_view(
    ctx,
    product_id: str | None,
    previous_event_type: str,
    previous_category: str,
    previous_product_id: str | None,
    previous_search_term: str | None,
    cart_content: list,
    customer_segment: str,
    session_affinity_categories: set,
    store_id: str,
    timestamp: pd.Timestamp,
) -> tuple:
    """
    Resolves which product and category to show on Product View.
    Returns (product_id, category, product_name, stock_status).
    """
    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map

    category = previous_category

    if product_id is None:
        if previous_event_type in ("Category View", "Product View"):
            if previous_category:
                product_id = get_random_product_from_category(ctx, previous_category)
                category = previous_category
            else:
                if previous_product_id:
                    category = product_category_map.get(previous_product_id)
                    product_id = get_random_product_from_category(ctx, category)

        elif previous_event_type == "Search View" and previous_search_term:
            matches = get_random_product_from_search_term(ctx, previous_search_term)
            product_id = random.choice(matches) if matches else None
            if product_id:
                category = product_category_map.get(product_id)

        elif previous_event_type == "Home View":
            category = get_segment_category(customer_segment)
            product_id = get_random_product_from_category(ctx, category)

        elif (
            previous_event_type in ("Add to Cart", "Cart View", "Remove from Cart")
            and cart_content
        ):
            anchor = random.choice(cart_content)
            anchor_category = product_category_map.get(anchor)

            # 70% stay within affinity of anchor category
            if random.random() < 0.7:
                # Build a local navigation cluster
                affinity_pool = {anchor_category} | set(
                    CATEGORY_AFFINITY.get(anchor_category, [])
                )
                # Intersect of categories in affinity pool with those in session intent
                candidates = list(affinity_pool & session_affinity_categories)
                category = (
                    random.choice(candidates)
                    if candidates
                    else get_segment_category(customer_segment)
                )

            # 30% does not co-relate to anchor category
            else:
                category = get_segment_category(customer_segment)

        else:
            category = get_segment_category(customer_segment)

    # Fallback
    if product_id is None:
        product_id = get_random_product_from_category(ctx, category) or random.choice(
            product_ids
        )

    if product_id is not None:
        category = product_category_map.get(product_id)

    product_name = product_name_map.get(product_id, None)
    stock_status = get_product_stock_status(ctx, store_id, product_id, timestamp)

    return product_id, category, product_name, stock_status


def resolve_category_view(
    previous_category: str | None,
    customer_segment: str,
    session_affinity_categories: set,
) -> str:
    """
    Resolves which category to navigate to.
    Returns category
    """
    if previous_category:
        # 70% stay within affinity of previous category
        if random.random() < 0.7:
            # Build a local navigation cluster
            affinity_pool = {previous_category} | set(
                CATEGORY_AFFINITY.get(previous_category, [])
            )
            # Intersect of categories in affinity pool with those in session intent
            candidates = list(affinity_pool & session_affinity_categories)
            return (
                random.choice(candidates)
                if candidates
                else get_segment_category(customer_segment)
            )
        return get_segment_category(customer_segment)

    if random.random() < 0.7 and session_affinity_categories:
        # Follow session intent only
        return random.choice(list(session_affinity_categories))

    # Fallback
    return get_segment_category(customer_segment)


def resolve_search_view(
    ctx,
    previous_category: str,
    session_affinity_categories: set,
) -> str:
    """
    Resolves the search term used.
    Returns search_term.
    """
    if random.random() < 0.6 and previous_category:
        # Bias search toward previous category items
        items = CATEGORY_ITEMS.get(previous_category, [])
        if items:
            return random.choice(items)

    # Bias search towards session affinity categories
    if random.random() < 0.7 and session_affinity_categories:
        cat = random.choice(list(session_affinity_categories))
        items = CATEGORY_ITEMS.get(cat, [])
        if items:
            return random.choice(items)

    # Fallback
    return get_search_term(ctx)


def resolve_payment_successful(
    ctx,
    cart_content: list,
    selected_promotions: list,
    mission_choice: str,
    has_treatment: bool,
    customer_segment: str,
) -> tuple:
    """
    Determines which items are purchased and removes them from cart.

    Business Logic:
    - Users may not purchase entire cart
    - Simulates real-world cart abandonment within checkout
    - Random subset of cart is purchased
    - Skewed towards more items being purchased

    Returns (purchased_items, updated_cart).
    """
    bundle_dict = ctx.bundles.bundle_dict

    # --- Determine Purchase Count ---
    alpha, beta = determine_purchase_alpha_beta(
        mission_choice, has_treatment, customer_segment
    )
    purchase_ratio = np.random.beta(alpha, beta)
    purchase_count = max(1, int(len(cart_content) * purchase_ratio))

    selected = []
    cart_counter: dict[str, int] = {}
    bundle_map = {}

    # Get bundle map
    for promo in selected_promotions:
        if promo.get("bundle_id"):
            bid = promo["bundle_id"]
            bundle_map[bid] = bundle_dict.get(bid, {})

    # Get cart item frequency map
    for item in cart_content:
        cart_counter[item] = cart_counter.get(item, 0) + 1

    # --- Decide Bundle Purchase ---
    for _, required_items in bundle_map.items():
        bundle_valid = all(
            cart_counter.get(pid, 0) >= qty for pid, qty in required_items.items()
        )
        if bundle_valid and random.random() < 0.7:
            # Strong bundle cohesion
            for pid, qty in required_items.items():
                selected.extend([pid] * qty)
                cart_counter[pid] -= qty

    # --- Decide Non Bundle Purchase ---
    remaining = []
    for pid, qty in cart_counter.items():
        remaining.extend([pid] * qty)

    still_needed = max(0, purchase_count - len(selected))
    if still_needed > 0 and remaining:
        selected.extend(random.sample(remaining, min(still_needed, len(remaining))))

    purchased_items = selected

    # Remove purchased item from cart
    updated_cart = cart_content.copy()
    for item in purchased_items:
        updated_cart.remove(item)

    return purchased_items, updated_cart
