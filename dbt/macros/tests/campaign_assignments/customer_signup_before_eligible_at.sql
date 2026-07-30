{% test customer_signup_before_eligible_at(
    model,
    customer_model
) %}

with assignments as (

    select *
    from {{ model }}

),

customers as (

    select *
    from {{ customer_model }}

)

select
    a.*

from assignments a

join customers c
    on a.customer_id = c.customer_id

where
    c.signup_date > a.eligible_at

{% endtest %}
