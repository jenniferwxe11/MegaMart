{{ config(materialized='table') }}

select
    transaction_id,
    product_id,
    product_name,
    category,
    quantity,
    unit_price,
    item_subtotal,
    item_discount,
    final_item_price
from {{ source('raw', 'transaction_items') }}
