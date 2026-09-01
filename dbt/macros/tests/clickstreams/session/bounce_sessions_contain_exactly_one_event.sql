{% test bounce_sessions_contain_exactly_one_event(model) %}

with session_summary as (

    select
        session_id,
        count(*) as event_count,
        max(cast(bounce_flag as int64)) as has_bounce
    from {{ model }}
    group by session_id

),

validation as (

    select *
    from session_summary
    where
        (has_bounce = 1 and event_count != 1)
        or
        (has_bounce = 0 and event_count = 1)

)

select *
from validation

{% endtest %}
