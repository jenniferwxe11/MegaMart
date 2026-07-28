{{ config(materialized='table') }}

select
    store_id,
    product_id,
    stock_status,
    stock_band,
    safe_cast(week_start_date as date) as week_start_date
from {{ source('raw', 'stock_snapshots') }}
