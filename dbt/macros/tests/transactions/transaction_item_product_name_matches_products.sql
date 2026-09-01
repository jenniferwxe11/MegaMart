{% test transaction_item_product_name_matches_products(model, product_model) %}

select
    ti.transaction_id,
    ti.product_id,
    ti.product_name,
    p.product_name as expected_product_name,
    ti.category,
    p.category as expected_category
from {{ model }} as ti
inner join {{ product_model }} as p
    on ti.product_id = p.product_id
where
    ti.product_name != p.product_name
    or ti.category != p.category

{% endtest %}
