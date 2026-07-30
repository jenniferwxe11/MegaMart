{{ config(materialized='table') }}

select
    competitor,
    product_id,
    product_name,
    brand,
    category,
    is_exclusive
from {{ source('raw', 'competitor_products') }}
