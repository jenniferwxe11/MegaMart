{% test review_date_after_transaction_date(model, transaction_model) %}

select
    r.review_id
from {{ model }} r
join {{ transaction_model }} t
    on r.transaction_id = t.transaction_id
where r.review_date < date(t.transaction_time)

{% endtest %}
