{% test remove_from_cart_reduces_cart_content_by_product(model) %}

with ordered_events as (

    select
        session_id,
        event_order,
        event_type,
        product_id,
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
    where event_type = 'Remove from Cart'

),

before_counts as (

    select
        session_id,
        event_order,
        product,
        count(*) as cnt_before
    from validation,
    unnest(coalesce(previous_cart_content, [])) as product
    group by 1,2,3

),

after_counts as (

    select
        session_id,
        event_order,
        product,
        count(*) as cnt_after
    from validation,
    unnest(coalesce(cart_content, [])) as product
    group by 1,2,3

),

comparison as (

    select
        coalesce(a.session_id, b.session_id) as session_id,
        coalesce(a.event_order, b.event_order) as event_order,
        coalesce(a.product, b.product) as product,
        coalesce(b.cnt_before, 0) as cnt_before,
        coalesce(a.cnt_after, 0) as cnt_after,
        v.product_id
    from after_counts a
    full outer join before_counts b
        using (session_id, event_order, product)
    join validation v
        on v.session_id = coalesce(a.session_id, b.session_id)
       and v.event_order = coalesce(a.event_order, b.event_order)

)

select *
from comparison
where

    -- Removed product must decrease by exactly one
    (product = product_id and cnt_after != cnt_before - 1)

    or

    -- All other products must remain unchanged
    (product != product_id and cnt_after != cnt_before)

{% endtest %}
