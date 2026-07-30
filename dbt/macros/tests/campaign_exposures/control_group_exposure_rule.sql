{% test control_group_exposure_rule(model) %}

select *

from {{ model }}

where
    assignment_group = 'Control'

    and (

        exposed = true

        or opened = true

        or clicked = true

        or exposed_time is not null

        or opened_time is not null

        or clicked_time is not null

        or cost_per_msg <> 0

    )

{% endtest %}
