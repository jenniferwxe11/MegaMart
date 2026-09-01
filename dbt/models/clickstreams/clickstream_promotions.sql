{{ config(materialized='table') }}

select
    c.clickstream_id,
    trim(replace(promotion_id, '"', '')) as promotion_id
from {{ ref('clickstreams') }} as c
cross join unnest(c.promotion_ids) as promotion_id
