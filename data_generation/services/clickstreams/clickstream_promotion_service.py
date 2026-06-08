import random

from data_generation.services.clickstreams.clickstream_transition_service import (
    promotion_engagement_probability,
    promotion_perception_accuracy,
)


def process_promotion_exposure(
    ctx,
    relevant_promotions: list,
    event_type: str,
    product_id,
    seen_promotions: dict,
    seen_promo_types: dict,
    selected_promotions: list,
    pending_events: list,
) -> tuple:
    """
    Handles the full promotion interaction pipeline for a single event:
      1. Records exposure (seen counts)
      2. Engagement gate (did the user notice it?)
      3. Perception gate (did they understand it?)
      4. Injects pending events for product/bundle promotions

    Mutates seen_promotions, seen_promo_types, selected_promotions, pending_events in place.

    Returns:
        (promotion_ids, bundle_ids) — lists of what was visible on the page
    """
    bundle_dict = ctx.bundles.bundle_dict

    if not relevant_promotions:
        return None, None

    # Record promotions encountered on page
    promotion_ids = [p["promotion_id"] for p in relevant_promotions]
    bundle_ids = [
        p["bundle_id"] for p in relevant_promotions if p.get("bundle_id") is not None
    ]

    # Determine user promotion interaction
    for promo in relevant_promotions:
        promotion_id = promo["promotion_id"]
        promotion_scope = promo.get("promotion_scope", None)
        promotion_mechanic = promo.get("promotion_mechanic", None)

        # --- Track exposure ---
        times_seen = seen_promotions.get(promotion_id, 0)
        seen_promotions[promotion_id] = times_seen + 1
        seen_promo_types[promotion_mechanic] = (
            seen_promo_types.get(promotion_mechanic, 0) + 1
        )

        # --- Engagement gate ---
        engagement_prob = promotion_engagement_probability(
            promo, event_type, times_seen
        )
        if random.random() >= engagement_prob:
            continue  # User does not engage with promotion

        # --- Perception gate ---
        perception_prob = promotion_perception_accuracy(promo)
        if random.random() >= perception_prob:
            continue  # User does not perceive promotion correctly

        selected_promotions.append(promo)

        # --- Inject pending events ---
        if promotion_scope == "product":
            if product_id == promo.get("promotion_target_id"):
                pending_events.append({"type": "Add to Cart", "product_id": product_id})

        elif promotion_scope == "bundle":
            bundle_id = promo["bundle_id"]
            bundle_products = bundle_dict.get(bundle_id, {})

            # Current product being viewed
            anchor_product_id = product_id

            # --- Step 1: Add anchor product first ---
            if anchor_product_id in bundle_products:
                for _ in range(bundle_products[anchor_product_id]):
                    pending_events.append(
                        {"type": "Add to Cart", "product_id": anchor_product_id}
                    )

            # --- Step 2: Add the rest of the bundle ---
            for bundle_product_id, quantity in bundle_products.items():

                # Skip anchor (already handled)
                if bundle_product_id == anchor_product_id:
                    continue

                pending_events.append(
                    {"type": "Product View", "product_id": bundle_product_id}
                )

                for _ in range(quantity):
                    pending_events.append(
                        {"type": "Add to Cart", "product_id": bundle_product_id}
                    )

    return promotion_ids, bundle_ids
