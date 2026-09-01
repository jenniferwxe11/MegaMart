{{ config(materialized='table') }}

select
    promotion_id,
    promotion_name,
    promotion_theme,
    campaign_id,
    promotion_mechanic,
    promotion_scope,
    promotion_target_id,
    promotion_value,
    min_spend,
    discount_code,
    priority,
    safe_cast(effective_start_date as date) as effective_start_date,
    safe_cast(effective_end_date as date) as effective_end_date
from {{ source('raw', 'promotions') }}
