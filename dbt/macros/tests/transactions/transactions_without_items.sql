{% test transactions_without_items(model, transaction_item_model) %}

select
    t.transaction_id
from {{ model }} as t
left join {{ transaction_item_model }} as ti
    on t.transaction_id = ti.transaction_id
where ti.transaction_id is null

{% endtest %}
