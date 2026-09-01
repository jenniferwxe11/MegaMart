{{ config(materialized='table') }}

select
    bundle_pricing_id,
    bundle_id,
    bundle_price,
    discount_value,
    pricing_phase,
    safe_cast(effective_start_date as date) as effective_start_date,
    safe_cast(effective_end_date as date) as effective_end_date
from {{ source('raw', 'bundle_pricings') }}
