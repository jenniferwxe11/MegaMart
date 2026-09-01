{% test basket_size_matches_items(model, transaction_item_model) %}

with item_counts as (

    select
        transaction_id,
        sum(quantity) as actual_basket_size
    from {{ transaction_item_model }}
    group by transaction_id

)

select
    t.transaction_id,
    t.basket_size,
    ic.actual_basket_size
from {{ model }} as t
inner join item_counts as ic
    on t.transaction_id = ic.transaction_id
where t.basket_size != ic.actual_basket_size

{% endtest %}
