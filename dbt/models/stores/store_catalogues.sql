{{ config(materialized='table') }}

select
    store_id,
    product_id,
    store_product_name,
    store_brand,
    store_category,
    store_selling_price
from {{ source('raw', 'store_catalogues') }}
