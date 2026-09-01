{% test payment_successful_reduces_cart_content_by_purchased_items(model) %}

with ordered_events as (

    select
        session_id,
        event_order,
        event_type,
        purchased_items,
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
    where event_type = 'Payment Successful'

),

previous_counts as (

    select
        session_id,
        event_order,
        product,
        count(*) as cnt_previous
    from validation,
    unnest(coalesce(previous_cart_content, [])) as product
    group by 1,2,3

),

purchased_counts as (

    select
        session_id,
        event_order,
        product,
        count(*) as cnt_purchased
    from validation,
    unnest(coalesce(purchased_items, [])) as product
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
        coalesce(a.session_id, p.session_id, c.session_id) as session_id,
        coalesce(a.event_order, p.event_order, c.event_order) as event_order,
        coalesce(a.product, p.product, c.product) as product,
        coalesce(c.cnt_previous, 0) as cnt_previous,
        coalesce(p.cnt_purchased, 0) as cnt_purchased,
        coalesce(a.cnt_after, 0) as cnt_after
    from after_counts a
    full outer join purchased_counts p
        using (session_id, event_order, product)
    full outer join previous_counts c
        using (session_id, event_order, product)

)

select *
from comparison
where cnt_after != cnt_previous - cnt_purchased

{% endtest %}
