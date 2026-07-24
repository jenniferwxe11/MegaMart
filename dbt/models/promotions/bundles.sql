{{ config(materialized='table') }}

select
    bundle_id,
    bundle_name,
    bundle_type,
    categories
from {{ source('raw', 'bundles') }}
