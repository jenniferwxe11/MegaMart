{{ config(materialized='table') }}

select
    c.clickstream_id,
    trim(replace(campaign_id, '"', '')) as campaign_id
from {{ ref('clickstreams') }} as c
cross join unnest(c.campaign_ids) as campaign_id
