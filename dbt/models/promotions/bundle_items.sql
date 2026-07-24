{{ config(materialized='table') }}

select
    bundle_id,
    product_id,
    quantity
from {{ source('raw', 'bundle_items') }}
