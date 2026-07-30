{{ config(materialized='table') }}

select
    competitor,
    product_id,
    scraped_product_name,
    scraped_category,
    scraped_price,
    has_active_promo,
    safe_cast(update_timestamp as timestamp) as update_timestamp
from {{ source('raw', 'competitor_price_history') }}
