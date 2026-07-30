{% test eligible_at_equal_campaign_start_date(
    model,
    campaign_model
) %}

with assignments as (

    select *
    from {{ model }}

),

campaigns as (

    select *
    from {{ campaign_model }}

)

select
    a.*

from assignments a

join campaigns c
    on a.campaign_id = c.campaign_id

where
    a.eligible_at <> c.start_date

{% endtest %}
