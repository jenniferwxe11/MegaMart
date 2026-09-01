{{ config(materialized='table') }}

select
    store_id,
    store_name,
    area,
    region,
    store_type
from {{ source('raw', 'stores') }}
