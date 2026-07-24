{% test discontinued_product_promotion_overlap(model) %}

select
    p.promotion_id,
    p.promotion_target_id,
    l.status,
    l.valid_from as lifecycle_start,
    l.valid_to as lifecycle_end,
    p.effective_start_date,
    p.effective_end_date

from {{ model }} p

join {{ ref('product_lifecycles') }} l
    on p.promotion_scope = 'product'
    and p.promotion_target_id = l.product_id

where
    l.status = 'Discontinued'
    and p.effective_start_date <= coalesce(l.valid_to, date '9999-12-31')
    and p.effective_end_date >= l.valid_from

{% endtest %}
