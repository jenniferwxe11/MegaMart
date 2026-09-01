{% test ab_campaign_contains_both_groups(
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
    where is_ab_test = true

),

summary as (

    select
        c.campaign_id,

        countif(a.assignment_group = 'Treatment') as treatment_count,
        countif(a.assignment_group = 'Control') as control_count

    from campaigns c

    left join assignments a
        on c.campaign_id = a.campaign_id

    group by c.campaign_id

)

select *

from summary

where
    treatment_count = 0
    or control_count = 0

{% endtest %}
