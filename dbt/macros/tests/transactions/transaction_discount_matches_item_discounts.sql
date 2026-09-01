{% test
    transaction_discount_matches_item_discounts(
        model,
        transaction_item_model
    )
%}





with discount_totals as (

    select
        transaction_id,
        sum(item_discount) as actual_total_discount
    from {{ transaction_item_model }}
    group by transaction_id

)

select
    t.transaction_id,
    t.total_discount,
    dt.actual_total_discount
from {{ model }} as t
inner join discount_totals as dt
    on t.transaction_id = dt.transaction_id
where abs(t.total_discount - dt.actual_total_discount) >= 0.01





{% endtest %}
