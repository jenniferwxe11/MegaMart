import math
import random

import pandas as pd

from data_generation.config.promotions_config import (
    DOLLAR_DISCOUNT_MAX_RATIO,
    PERCENTAGE_DISCOUNT_MAX_PCT,
)
from data_generation.config.transactions_config import DISCOUNT_PROB_BY_SEGMENT
from data_generation.services.transactions.transaction_lookup_service import (
    get_active_bundle_pricing,
)

# -------------------------------
# Promotion Application Functions
# -------------------------------


def is_bundle_valid(ctx, bundle_id, cart_items):
    """
    Validates whether a bundle discount can be applied.

    Criteria:
    - Bundle promotions require specific product combinations
    """
    bundle_dict = ctx.bundles.bundle_dict

    required_items = bundle_dict.get(bundle_id, {})

    if not required_items:
        return False

    cart_map = {item["product_id"]: item["quantity"] for item in cart_items}

    for product_id, required_quantity in required_items.items():
        if cart_map.get(product_id, 0) < required_quantity:
            return False

    return True


def get_eligible_promotions(ctx, transaction_time, cart_items, cart_subtotal):
    """
    Identifies all eligible promotions for a given transaction.

    Validation Criteria:
    - Time validity (promotion active window)
    - Scope matching:
        - Cart-level promotions
        - Category-level promotions
        - Product-level promotions
        - Bundle eligibility (required item combinations)
    """
    promotions_df = ctx.promotions.promotions_df

    # Parse time
    transaction_time = pd.Timestamp(transaction_time)

    # Filter active promotions
    valid_promotions = promotions_df[
        (promotions_df["effective_start_date"] <= transaction_time)
        & (promotions_df["effective_end_date"] >= transaction_time)
    ]

    eligible_promotions = []

    for _, promo in valid_promotions.iterrows():
        scope = promo["promotion_scope"]
        target = promo["promotion_target_id"]
        min_spend = promo["min_spend"]

        # Filter min spend
        if pd.isna(min_spend) or cart_subtotal >= min_spend:

            # --- Scope Matching ---
            if scope == "cart":
                eligible_promotions.append(promo.to_dict())

            elif scope == "category":
                if any(item["category"] == target for item in cart_items):
                    eligible_promotions.append(promo.to_dict())

            elif scope == "product":
                if any(item["product_id"] == target for item in cart_items):
                    eligible_promotions.append(promo.to_dict())

            elif scope == "bundle":
                # Check bundle composition
                if is_bundle_valid(ctx, target, cart_items):
                    eligible_promotions.append(promo.to_dict())

    if not eligible_promotions:
        return []

    return sorted(eligible_promotions, key=lambda x: x["priority"], reverse=True)


def select_shipping_promo(eligible_promotions, cart_subtotal):
    """
    Selects the best eligible free shipping promotion.

    Selection Rule:
    - Cart subtotal fulfills min spend
    - Lowest min spend requirement
    """
    shipping_promos = [
        p for p in eligible_promotions if p["promotion_mechanic"] == "free_shipping"
    ]

    if not shipping_promos:
        return None

    valid = [
        p
        for p in shipping_promos
        if pd.isna(p["min_spend"]) or cart_subtotal >= p["min_spend"]
    ]

    if not valid:
        return None

    return min(valid, key=lambda x: x["min_spend"])


def is_overlap(
    ctx,
    promo_a,
    promo_b,
    cart_items,
):
    """
    Checks if two promotion conflict (cannot be applied together).

    Overlap cases:
    - Same product or category targeted
    - Product vs category match within cart
    - Bundle item overlaps with product/category in cart
    - Bundle vs bundle shares common items
    """
    bundle_dict = ctx.bundles.bundle_dict

    scope_a = promo_a["promotion_scope"]
    scope_b = promo_b["promotion_scope"]

    target_a = promo_a["promotion_target_id"]
    target_b = promo_b["promotion_target_id"]

    # --- Bundle vs Bundle ---
    if scope_a == "bundle" and scope_b == "bundle":
        bundle_items_a = bundle_dict.get(target_a, {})
        bundle_items_b = bundle_dict.get(target_b, {})
        return bool(set(bundle_items_a) & set(bundle_items_b))

    # --- Bundle vs Product ---
    if scope_a == "bundle" and scope_b == "product":
        bundle_items = bundle_dict.get(target_a, {})
        return target_b in bundle_items

    if scope_b == "bundle" and scope_a == "product":
        bundle_items = bundle_dict.get(target_b, {})
        return target_a in bundle_items

    # --- Bundle vs Category ---
    if scope_a == "bundle" and scope_b == "category":
        bundle_items = bundle_dict.get(target_a, {})
        return any(
            item["product_id"] in bundle_items and item["category"] == target_b
            for item in cart_items
        )

    if scope_b == "bundle" and scope_a == "category":
        bundle_items = bundle_dict.get(target_b, {})
        return any(
            item["product_id"] in bundle_items and item["category"] == target_a
            for item in cart_items
        )

    # --- Product vs Category ---
    if scope_a == "product" and scope_b == "category":
        return any(
            item["product_id"] == target_a and item["category"] == target_b
            for item in cart_items
        )
    if scope_b == "product" and scope_a == "category":
        return any(
            item["product_id"] == target_b and item["category"] == target_a
            for item in cart_items
        )

    # --- Product vs Product ---
    if scope_a == "product" and scope_b == "product":
        return target_a == target_b

    # --- Category vs Category ---
    if scope_a == "category" and scope_b == "category":
        return target_a == target_b

    return False


def should_use_promo(customer_segment, cart_subtotal):
    """
    Decides whether to use a promotion.

    Factors:
    - Customer segment
    - Cart subtotal
    """
    base_min, base_max = DISCOUNT_PROB_BY_SEGMENT.get(customer_segment, (0.5, 0.7))
    base_prob = random.uniform(base_min, base_max)

    # numerical safety clamp (prevents overflow edge cases)
    x = 0.05 * (cart_subtotal - 80)

    # prevent extreme exp blowups
    x = max(min(x, 50), -50)

    boost = 1 / (1 + math.exp(x))

    base_prob += 0.2 * boost

    return min(base_prob, 1)


def opt_for_delivery(
    ctx,
    customer_id,
    store_id,
    shipping_promo,
    cart_subtotal,
):
    """
    Determines whether a customer opts for delivery or pickup for in-store transactions.

    Factors:
    - Base likelihood of choosing delivery
    - Presence of free shipping promotions (increases likelihood)
    - Distance between customer and store (area/region mismatch)
    - Whether cart meets minimum spend for the best free shipping promo
    - Higher cart value (larger baskets are more likely to be delivered)
    """
    customer_area_map = ctx.customers.customer_area_map
    customer_region_map = ctx.customers.customer_region_map
    store_area_map = ctx.stores.store_area_map
    store_region_map = ctx.stores.store_region_map

    base_prob = 0.15

    if shipping_promo:
        base_prob += 0.3

    # --- Distance Effect ---
    customer_area = customer_area_map.get(customer_id, None)
    store_area = store_area_map.get(store_id, None)
    customer_region = customer_region_map.get(customer_id, None)
    store_region = store_region_map.get(store_id, None)

    if customer_region != store_region:
        base_prob += 0.2
    if customer_area != store_area:
        base_prob += 0.1

    # Large cart/high value
    if cart_subtotal > 100:
        base_prob += 0.1

    base_prob = min(base_prob, 0.85)

    return random.random() < base_prob


def is_promotion_viable(promo, eligible_items):
    """
    Guards against promotions whose value is disproportionate to the
    eligible basket — which is not realistic in a supermarket context.

    Dollar discount:
    - Product Scope: Skip if discount >= subtotal OR discount > 40 % of subtotal
    - Category Scope: Skip if discount >= category_subtotal OR discount > 40 % of category_subtotal

    Percentage discount:
    - Skip if percentage discount > 40%
    """
    if not eligible_items:
        return False

    mechanic = promo["promotion_mechanic"]
    scope = promo["promotion_scope"]
    discount_value = promo["promotion_value"]

    # --- Percentage Discount Cap ---
    if mechanic == "percentage_discount":
        if discount_value > PERCENTAGE_DISCOUNT_MAX_PCT:
            return False

    # --- Dollar Discount Cap ---
    elif mechanic == "dollar_discount":
        if scope == "product":
            # Only one product
            item = eligible_items[0]
            line_subtotal = round(item["price"] * item["quantity"], 2)

            # Skip if discount wipes out the line or exceeds the ratio cap
            if discount_value >= line_subtotal:
                return False
            if discount_value > line_subtotal * DOLLAR_DISCOUNT_MAX_RATIO:
                return False

        elif scope == "category":
            category_subtotal = round(
                sum(item["price"] * item["quantity"] for item in eligible_items), 2
            )

            # Skip if discount wipes out the whole category basket or exceeds the ratio cap
            if discount_value >= category_subtotal:
                return False
            if discount_value > category_subtotal * DOLLAR_DISCOUNT_MAX_RATIO:
                return False

    return True


def apply_cart_level_discount(
    ctx,
    cart_items,
    promotion_id,
    transaction_time,
):
    """
    Applies promotion or bundle discount to the cart.

    Criteria:
    - Promotion validity window
    - Minimum spend requirement
    - Scope (product/category level targeting)
    - Bundle eligibility
    """
    promotions_df = ctx.promotions.promotions_df
    bundle_dict = ctx.bundles.bundle_dict

    if not promotion_id:
        return 0, {}

    promo_row = promotions_df[promotions_df["promotion_id"] == promotion_id]
    if promo_row.empty:
        return 0, {}

    promo = promo_row.iloc[0]

    # --- Date Validation ---
    transaction_time = pd.Timestamp(transaction_time)

    if (
        transaction_time < promo["effective_start_date"]
        or transaction_time > promo["effective_end_date"]
    ):
        return 0, {}

    # --- Scope Validation ---
    if promo["promotion_scope"] == "product":
        eligible_items = [
            item
            for item in cart_items
            if item["product_id"] == promo["promotion_target_id"]
        ]

    elif promo["promotion_scope"] == "category":
        eligible_items = [
            item
            for item in cart_items
            if item["category"] == promo["promotion_target_id"]
        ]

    elif promo["promotion_scope"] == "bundle":
        # Get only bundle items in cart
        eligible_items = [
            item
            for item in cart_items
            if item["product_id"] in bundle_dict[promo["promotion_target_id"]]
        ]

    else:
        return 0, {}

    if not eligible_items:
        return 0, {}

    # --- Promotion Viability ---
    if promo["promotion_mechanic"] in ("dollar_discount", "percentage_discount"):
        if not is_promotion_viable(promo, eligible_items):
            return 0, {}

    # --- Compute Discount ---
    eligible_subtotal = sum(item["price"] * item["quantity"] for item in eligible_items)

    if promo["promotion_mechanic"] == "percentage_discount":
        discount = eligible_subtotal * (promo["promotion_value"] / 100)

    elif promo["promotion_mechanic"] == "dollar_discount":
        discount = min(promo["promotion_value"], eligible_subtotal)

    elif promo["promotion_mechanic"] == "bundle":
        bundle_pricing = get_active_bundle_pricing(
            ctx, promo["promotion_target_id"], transaction_time
        )
        if bundle_pricing is None:
            return 0, {}

        discount = max(eligible_subtotal - bundle_pricing["bundle_price"], 0)

    else:
        discount = 0

    # --- Discount Allocation ---
    allocation = {}

    if discount > 0 and eligible_subtotal > 0:

        rounded_discount = round(discount, 2)

        allocated = 0

        for item in eligible_items[:-1]:
            item_total = item["price"] * item["quantity"]
            share = item_total / eligible_subtotal

            value = round(rounded_discount * share, 2)

            allocation[item["product_id"]] = value
            allocated += value

        # Give the remaining cents to the last item
        last = eligible_items[-1]

        allocation[last["product_id"]] = round(
            rounded_discount - allocated,
            2,
        )

        discount = rounded_discount

    return discount, allocation


def resolve_promotion_stack(
    ctx,
    customer_segment,
    promotions,
    cart_items,
    transaction_time,
    cart_subtotal,
    transaction_type,
):
    """
    Resolves which promotions can be applied together.

    Rules:
    - Priority decides baseline selection (Bundle > Product > Category)
    - If overlap, compare total discount of conflicting promo vs new promo
    """
    # Sort promotions by priority
    promotions = sorted(promotions, key=lambda x: -x["priority"])

    selected = []

    # See if promotion is compatible with already selected promotions
    for promo in promotions:
        conflicting = [s for s in selected if is_overlap(ctx, promo, s, cart_items)]
        if conflicting:

            # Calculate discount value
            new_discount, _ = apply_cart_level_discount(
                ctx,
                cart_items,
                promo["promotion_id"],
                transaction_time,
            )
            old_discount = 0
            for c in conflicting:
                d, _ = apply_cart_level_discount(
                    ctx,
                    cart_items,
                    c["promotion_id"],
                    transaction_time,
                )
                old_discount += d

            # --- Decision ---
            if new_discount > old_discount:

                # Online: User may or may not pick best promo
                if transaction_type == "Online":
                    if random.random() < should_use_promo(
                        customer_segment, cart_subtotal
                    ):
                        # Choose best promo
                        for c in conflicting:
                            selected.remove(c)
                        selected.append(promo)
                    # Else: Choose suboptimal promo (do nothing)

                # In store: POS will always choose best promo
                elif transaction_type == "In Store":
                    # Choose best promo
                    for c in conflicting:
                        selected.remove(c)
                    selected.append(promo)

        else:
            selected.append(promo)

    return selected
