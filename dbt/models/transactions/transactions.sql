{{ config(materialized='table') }}

select
    transaction_id,
    customer_id,
    store_id,
    cart_subtotal,
    total_discount,
    shipping_fee,
    shipping_discount,
    transaction_total,
    payment_method,
    basket_size,
    num_unique_items,
    applied_promotions,
    safe_cast(transaction_time as timestamp) as transaction_time
from {{ source('raw', 'transactions') }}
