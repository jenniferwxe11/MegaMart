{% test single_current_product_content_quality_version(model) %}

select
    product_id
from {{ model }}
group by product_id
having sum(case when is_current = true then 1 else 0 end) != 1

{% endtest %}
