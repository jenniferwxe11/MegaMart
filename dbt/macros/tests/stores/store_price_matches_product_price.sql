{% test store_price_matches_product_price(model, tolerance=0.2) %}

select
    s.store_id,
    s.product_id
from {{ model }} s
join {{ ref('products') }} p
using(product_id)
where abs(s.store_selling_price - p.selling_price)
      / p.selling_price > {{ tolerance }}

{% endtest %}
