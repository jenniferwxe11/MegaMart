{{ config(materialized='table') }}

select
    campaign_id,
    customer_id,
    assignment_group,
    safe_cast(eligible_at as date) as eligible_at
from {{ source('raw', 'campaign_assignments') }}
