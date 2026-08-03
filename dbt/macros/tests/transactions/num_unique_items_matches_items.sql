{% test num_unique_items_matches_items(model, transaction_item_model) %}

with unique_item_counts as (

    select
        transaction_id,
        count(distinct product_id) as actual_num_unique_items
    from {{ transaction_item_model }}
    group by transaction_id

)

select
    t.transaction_id,
    t.num_unique_items,
    uic.actual_num_unique_items
from {{ model }} as t
inner join unique_item_counts as uic
    on t.transaction_id = uic.transaction_id
where t.num_unique_items != uic.actual_num_unique_items

{% endtest %}
