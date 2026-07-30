{{ config(materialized='table') }}

select
    campaign_id,
    campaign_name,
    campaign_type,
    target_segment,
    season,
    channels,
    budget,
    is_ab_test,
    status,
    safe_cast(start_date as date) as start_date,
    safe_cast(end_date as date) as end_date
from {{ source('raw', 'campaigns') }}
