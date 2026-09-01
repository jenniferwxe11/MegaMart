{{ config(materialized='table') }}

select
    store_id,
    product_id,
    delta,
    reason,
    stock_after,
    safe_cast(event_timestamp as timestamp) as event_timestamp
from {{ source('raw', 'inventory_change_events') }}
