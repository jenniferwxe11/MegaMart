{{ config(materialized='table') }}

select
    clickstream_id,
    session_id,
    customer_id,
    customer_segment,
    campaign_ids,
    has_treatment_campaign,
    has_control_campaign,
    device_category,
    referrer,
    location,
    event_order,
    event_type,
    page,
    scroll_depth,
    product_id,
    product_name,
    category,
    promotion_ids,
    bundle_ids,
    bounce_flag,
    cart_size,
    cart_content,
    purchased_items,
    stock_status,
    safe_cast(event_timestamp as timestamp) as event_timestamp
from {{ source('raw', 'clickstreams') }}
