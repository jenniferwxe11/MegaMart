{% test purchased_item_subset_previous_cart_content(model) %}

with ordered_events as (

    select
        session_id,
        event_order,
        event_type,
        purchased_items,
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

)

select
    p.session_id,
    p.event_order,
    p.product,
    p.cnt_purchased,
    coalesce(c.cnt_previous, 0) as cnt_previous
from purchased_counts p
left join previous_counts c
    using (session_id, event_order, product)
where p.cnt_purchased > coalesce(c.cnt_previous, 0)

{% endtest %}
