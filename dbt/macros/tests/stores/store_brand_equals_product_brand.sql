{% test store_brand_equals_product_brand(model) %}

select
    s.store_id,
    s.product_id
from {{ model }} s
join {{ ref('products') }} p
using(product_id)
where lower(trim(s.store_brand))
      != lower(trim(p.brand))

{% endtest %}
