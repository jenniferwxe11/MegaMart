{% test review_date_after_transaction_date(model, mapping_model) %}

select
    r.review_id
from {{ model }} r
join {{ mapping_model }} t
    on r.transaction_id = t.transaction_id
where r.review_date < date(t.transaction_time)

{% endtest %}
