{% test cart_content_matches_previous_after_non_cart_events(model) %}

with ordered_events as (

    select
        session_id,
        event_order,
        event_type,
        cart_content,
        lag(cart_content) over (
            partition by session_id
            order by event_order
        ) as previous_cart_content
    from {{ model }}

),

validation as (

    select *
    from ordered_events
    where
        previous_cart_content is not null
        and event_type not in (
            'Add to Cart',
            'Remove from Cart',
            'Payment Successful'
        )

)

select *
from validation
where

    array_length(cart_content)
        != array_length(previous_cart_content)

    or exists (

        select 1
        from unnest(previous_cart_content) p
        where p not in (
            select c
            from unnest(cart_content) c
        )

    )

    or exists (

        select 1
        from unnest(cart_content) c
        where c not in (
            select p
            from unnest(previous_cart_content) p
        )

    )

{% endtest %}
