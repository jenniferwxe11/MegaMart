{{ config(materialized='table') }}

select
    t.transaction_id,
    trim(replace(json_value(promotion, '$.promotion_id'), '"', ''))
        as promotion_id,
    json_value(promotion, '$.promotion_type') as promotion_type,
    safe_cast(json_value(promotion, '$.amount') as numeric) as amount
from {{ ref('transactions') }} as t,
    unnest(t.applied_promotions) as promotion
