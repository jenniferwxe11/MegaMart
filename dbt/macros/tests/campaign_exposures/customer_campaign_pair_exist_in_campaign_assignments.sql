{% test customer_campaign_pair_exist_in_campaign_assignments(
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

left join assignments a
    on e.customer_id = a.customer_id
   and e.campaign_id = a.campaign_id

where
    a.customer_id is null

{% endtest %}
