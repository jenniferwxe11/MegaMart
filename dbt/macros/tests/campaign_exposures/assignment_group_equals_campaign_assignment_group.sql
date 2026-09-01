{% test assignment_group_equals_campaign_assignment_group(
    model,
    campaign_assignment_model
) %}

with exposures as (

    select *
    from {{ model }}

),

assignments as (

    select *
    from {{ campaign_assignment_model }}

)

select
    e.*

from exposures e

join assignments a
    on e.customer_id = a.customer_id
   and e.campaign_id = a.campaign_id

where
    e.assignment_group <> a.assignment_group

{% endtest %}
