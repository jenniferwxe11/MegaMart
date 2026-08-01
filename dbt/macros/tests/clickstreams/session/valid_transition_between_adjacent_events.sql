{% test valid_transition_between_adjacent_events(model) %}

with ordered_events as (

    select
        session_id,
        event_order,
        event_type,
        lag(event_type) over (
            partition by session_id
            order by event_order
        ) as previous_event
    from {{ model }}

),

validation as (

    select *
    from ordered_events
    where previous_event is not null
      and not (

        (previous_event = 'Home View'
            and event_type in (
                'Product View',
                'Category View',
                'Search View',
                'Cart View'
            ))

        or

        (previous_event = 'Category View'
            and event_type in (
                'Product View',
                'Search View',
                'Category View',
                'Home View',
                'Cart View'
            ))

        or

        (previous_event = 'Search View'
            and event_type in (
                'Product View',
                'Category View',
                'Search View',
                'Home View',
                'Cart View'
            ))

        or

        (previous_event = 'Product View'
            and event_type in (
                'Add to Cart',
                'Category View',
                'Search View',
                'Home View',
                'Product View',
                'Cart View'
            ))

        or

        (previous_event = 'Add to Cart'
            and event_type in (
                'Add to Cart',
                'Cart View',
                'Product View',
                'Category View',
                'Home View',
                'Search View'
            ))

        or

        (previous_event = 'Cart View'
            and event_type in (
                'Checkout Start',
                'Product View',
                'Remove from Cart',
                'Home View',
                'Category View',
                'Search View'
            ))

        or

        (previous_event = 'Remove from Cart'
            and event_type in (
                'Cart View',
                'Product View',
                'Home View',
                'Category View',
                'Search View'
            ))

        or

        (previous_event = 'Checkout Start'
            and event_type in (
                'Payment Attempt',
                'Cart View',
                'Home View'
            ))

        or

        (previous_event = 'Payment Attempt'
            and event_type in (
                'Payment Successful',
                'Payment Failed'
            ))

        or

        (previous_event = 'Payment Successful'
            and event_type in (
                'Home View',
                'Category View',
                'Product View'
            ))

        or

        (previous_event = 'Payment Failed'
            and event_type in (
                'Payment Attempt',
                'Cart View',
                'Home View'
            ))

      )

)

select *
from validation

{% endtest %}
