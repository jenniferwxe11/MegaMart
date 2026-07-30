{% test non_ab_campaigns_have_only_treatment(
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
    where is_ab_test = false

)

select
    a.*

from assignments a

join campaigns c
    on a.campaign_id = c.campaign_id

where
    assignment_group <> 'Treatment'

{% endtest %}
