{% test customer_type_only_in_online_only_or_omnichannel(
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
    a.*,
    c.customer_type

from assignments a

join customers c
    on a.customer_id = c.customer_id

where
    c.customer_type not in (
        'Online Only',
        'Omnichannel'
    )

{% endtest %}
