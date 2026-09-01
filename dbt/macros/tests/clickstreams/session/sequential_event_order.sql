{% test sequential_event_order(model) %}

with ordered_events as (

    select
        session_id,
        event_order,
        row_number() over (
            partition by session_id
            order by event_order
        ) as expected_event_order
    from {{ model }}

),

validation as (

    select *
    from ordered_events
    where event_order != expected_event_order

)

select *
from validation

{% endtest %}
