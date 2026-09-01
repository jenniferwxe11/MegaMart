{% test product_information_matches_product_table(model, product_model) %}

select
    c.clickstream_id,
    c.product_id,
    c.product_name,
    c.category,
    p.product_name as expected_product_name,
    p.category as expected_category
from {{ model }} c
inner join {{ product_model }} p
    on c.product_id = p.product_id
where
    c.product_id is not null
    and (
        c.product_name != p.product_name
        or c.category != p.category
    )

{% endtest %}
