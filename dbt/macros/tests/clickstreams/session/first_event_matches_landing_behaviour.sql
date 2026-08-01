{% test first_event_matches_landing_behaviour(model) %}

with validation as (

    select *
    from {{ model }}
    where
        event_order = 1
        and not (

            (referrer = 'organic_search'
                and event_type in (
                    'Home View',
                    'Search View',
                    'Product View'
                ))

            or

            (referrer = 'direct'
                and event_type in (
                    'Home View',
                    'Category View',
                    'Product View'
                ))

            or

            (referrer = 'social_media'
                and event_type in (
                    'Home View',
                    'Product View',
                    'Category View'
                ))

            or

            (referrer = 'email'
                and event_type in (
                    'Home View',
                    'Product View',
                    'Category View'
                ))

            or

            (referrer = 'unknown'
                and event_type in (
                    'Home View',
                    'Product View',
                    'Category View',
                    'Search View'
                ))

        )

)

select *
from validation

{% endtest %}
