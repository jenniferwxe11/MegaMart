{% test promotion_type_matches_promotions(model, promotion_model) %}

select
    tp.transaction_id,
    tp.promotion_id,
    tp.promotion_type,
    p.promotion_mechanic as expected_promotion_type
from {{ model }} as tp
inner join {{ promotion_model }} as p
    on tp.promotion_id = p.promotion_id
where tp.promotion_type != p.promotion_mechanic

{% endtest %}
