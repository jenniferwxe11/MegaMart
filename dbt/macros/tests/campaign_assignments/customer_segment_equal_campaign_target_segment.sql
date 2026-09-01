{% test customer_segment_equal_campaign_target_segment(
    model,
    customer_model,
    campaign_model
) %}

with assignments as (

    select *
    from {{ model }}

),

customers as (

    select *
    from {{ customer_model }}

),

campaigns as (

    select *
    from {{ campaign_model }}

)

select
    a.*,
    cu.customer_segment,
    c.target_segment

from assignments a

join customers cu
    on a.customer_id = cu.customer_id

join campaigns c
    on a.campaign_id = c.campaign_id

where
    cu.customer_segment <> c.target_segment

{% endtest %}
