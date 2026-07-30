{% test channel_matches_campaign_channels(
    model,
    campaign_model
) %}

with exposures as (

    select *
    from {{ model }}

),

campaigns as (

    select *
    from {{ campaign_model }}

)

select
    e.*

from exposures e

join campaigns c
    on e.campaign_id = c.campaign_id

where
    not (
        e.channel in unnest(c.channels)
    )

{% endtest %}
