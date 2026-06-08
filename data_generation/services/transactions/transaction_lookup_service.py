import random

from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_location,
)

# ------------------------------
# Data Access & Lookup Functions
# ------------------------------


def get_store(ctx, customer_id):
    """
    Assigns a store for in-store transactions based on customer location.

    Logic:
    - Known customers are more likely to shop within their usual area
    - Nearby stores (same region) are occasionally selected
    - A small proportion of transactions are random (walk-ins, travel, anomalies)
    """
    stores_df = ctx.stores.stores_df
    retail_store_ids = ctx.stores.retail_store_ids

    area = get_location(ctx, customer_id)
    store_candidates = stores_df[stores_df["area"] == area]["store_id"].tolist()

    if store_candidates:
        store_id = random.choice(store_candidates)
    else:
        store_id = random.choice(retail_store_ids)

    return store_id


def get_shipping_fee(
    ctx,
    store_id,
    customer_id,
):
    customer_area_map = ctx.customers.customer_area_map
    customer_region_map = ctx.customers.customer_region_map
    store_area_map = ctx.stores.store_area_map
    store_region_map = ctx.stores.store_region_map
    online_store_id = ctx.stores.online_store_id

    customer_area = customer_area_map.get(customer_id, None)
    store_area = store_area_map.get(store_id, None)
    customer_region = customer_region_map.get(customer_id, None)
    store_region = store_region_map.get(store_id, None)

    if store_id == online_store_id:
        base_fee = 8
    else:  # In store delivery
        base_fee = 4

    # Distance adjustment
    if customer_region != store_region:
        base_fee += 8
    elif customer_area != store_area:
        base_fee += 4

    shipping_fee = random.uniform(base_fee, base_fee + 2)
    return shipping_fee


def get_active_bundle_pricing(ctx, bundle_id, transaction_date):
    """
    Returns the active bundle pricing row for a bundle_id at a given time.
    """
    bundle_pricings_df = ctx.bundles.bundle_pricings_df

    active_rows = bundle_pricings_df[
        (bundle_pricings_df["bundle_id"] == bundle_id)
        & (bundle_pricings_df["effective_start_date"] <= transaction_date)
        & (bundle_pricings_df["effective_end_date"] >= transaction_date)
    ]

    if active_rows.empty:
        return None

    row = active_rows.sort_values("effective_start_date", ascending=False).iloc[0]

    # In case of overlaps, pick most recent or highest priority
    return {
        "bundle_id": row["bundle_id"],
        "bundle_price": row["bundle_price"],
        "effective_start_date": row["effective_start_date"],
        "effective_end_date": row["effective_end_date"],
    }
