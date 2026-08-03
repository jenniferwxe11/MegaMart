{% test store_category_equals_product_category(model) %}

select
    s.store_id,
    s.product_id
from {{ model }} s
join {{ ref('products') }} p
using(product_id)
where s.store_category != p.category

{% endtest %}
