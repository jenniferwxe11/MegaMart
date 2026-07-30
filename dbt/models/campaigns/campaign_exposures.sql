{{ config(materialized='table') }}

select
    customer_id,
    campaign_id,
    channel,
    assignment_group,
    eligible,
    exposed,
    opened,
    clicked,
    device_platform,
    cost_per_msg,
    safe_cast(exposed_time as timestamp) as exposed_time,
    safe_cast(opened_time as timestamp) as opened_time,
    safe_cast(clicked_time as timestamp) as clicked_time
from {{ source('raw', 'campaign_exposures') }}
