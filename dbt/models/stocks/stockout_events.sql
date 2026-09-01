{{ config(materialized='table') }}

select
    store_id,
    product_id,
    safe_cast(stockout_start_date as date) as stockout_start_date,
    safe_cast(stockout_end_date as date) as stockout_end_date
from {{ source('raw', 'stockout_events') }}
