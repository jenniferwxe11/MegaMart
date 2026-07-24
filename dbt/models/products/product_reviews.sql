{{ config(materialized='table') }}

select
    review_id,
    transaction_id,
    product_id,
    customer_id,
    rating,
    review_text,
    safe_cast(review_date as date) as review_date
from {{ source('raw', 'product_reviews') }}
