{{ config(materialized='table') }}

select
    product_id,
    status,
    is_current,
    safe_cast(launch_date as date) as launch_date,
    safe_cast(discontinuation_date as date) as discontinuation_date,
    safe_cast(valid_from as date) as valid_from,
    safe_cast(valid_to as date) as valid_to
from {{ source('raw', 'product_lifecycles') }}
