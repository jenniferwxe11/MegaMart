{% test
    product_view_category_equals_promotion_target_id(
        model,
        promotion_model
    )
%}




select distinct
    c.clickstream_id,
    c.category,
    promotion_id,
    p.promotion_target_id
from {{ model }} c
cross join unnest(c.promotion_ids) as promotion_id
inner join {{ promotion_model }} p
    on promotion_id = p.promotion_id
where
    c.event_type = 'Product View'
    and p.promotion_scope = 'Category'
    and c.category != p.promotion_target_id




{% endtest %}
