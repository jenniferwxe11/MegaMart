{% test device_platform_equals_customer_device_platform(
    model,
    customer_model
) %}

with exposures as (

    select *
    from {{ model }}

),

customers as (

    select *
    from {{ customer_model }}

)

select
    e.*

from exposures e

join customers c
    on e.customer_id = c.customer_id

where
    e.device_platform <> c.device_platform

{% endtest %}
