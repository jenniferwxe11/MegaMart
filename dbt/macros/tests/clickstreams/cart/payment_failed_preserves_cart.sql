{% test payment_failed_preserves_cart(model) %}

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
        event_type = 'Payment Failed'

)

select *
from validation
where

    previous_cart_content is null

    or array_length(cart_content)
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
