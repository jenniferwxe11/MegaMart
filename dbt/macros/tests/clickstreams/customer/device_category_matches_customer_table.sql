{% test device_category_matches_customer_table(model, customer_model) %}

select
    c.clickstream_id,
    c.customer_id,
    c.device_category as clickstream_device_category,
    cu.device_category as customer_table_device_category
from {{ model }} c
inner join {{ customer_model }} cu
    on c.customer_id = cu.customer_id
where c.device_category != cu.device_category

{% endtest %}
