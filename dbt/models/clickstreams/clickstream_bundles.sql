{{ config(materialized='table') }}

select
    c.clickstream_id,
    trim(replace(bundle_id, '"', '')) as bundle_id
from {{ ref('clickstreams') }} as c
cross join unnest(c.bundle_ids) as bundle_id
