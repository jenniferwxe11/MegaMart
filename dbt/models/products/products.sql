{{ config(materialized='table') }}

select
    product_id,
    product_name,
    brand,
    category,
    selling_price,
    cost_price
from {{ source('raw', 'products') }}
