{% test single_current_product_lifecycle_version(model) %}

select
    product_id
from {{ model }}
where is_current = true
group by product_id
having count(*) > 1

{% endtest %}
