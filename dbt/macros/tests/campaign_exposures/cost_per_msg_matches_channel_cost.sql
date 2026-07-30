{% test cost_per_msg_matches_channel_cost(model) %}

select *

from {{ model }}

where

    (

        exposed = false

        and cost_per_msg <> 0

    )

    or

    (

        exposed = true

        and (

            (channel = 'Email' and cost_per_msg <> 0.02)

            or

            (channel = 'SMS' and cost_per_msg <> 0.05)

            or

            (channel = 'Push Notifications'
                and cost_per_msg <> 0.01)

            or

            (channel = 'In-App'
                and cost_per_msg <> 0)

            or

            (channel = 'Paid Advertisements'
                and cost_per_msg <> 1)

        )

    )

{% endtest %}
