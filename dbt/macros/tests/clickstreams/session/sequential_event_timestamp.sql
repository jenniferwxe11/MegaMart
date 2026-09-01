{% test sequential_event_timestamp(model) %}

with ordered_events as (

    select
        session_id,
        event_order,
        event_timestamp,
        lag(event_timestamp) over (
            partition by session_id
            order by event_order
        ) as previous_event_timestamp
    from {{ model }}

),

validation as (

    select *
    from ordered_events
    where previous_event_timestamp is not null
      and event_timestamp < previous_event_timestamp

)

select *
from validation

{% endtest %}
