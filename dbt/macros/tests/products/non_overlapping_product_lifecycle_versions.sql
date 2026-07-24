{% test non_overlapping_product_lifecycle_versions(model) %}

select
    a.product_id
from {{ model }} a
join {{ model }} b
    on a.product_id = b.product_id
   and a.valid_from < coalesce(b.valid_to,'9999-12-31')
   and coalesce(a.valid_to,'9999-12-31') > b.valid_from
   and a.valid_from <> b.valid_from

{% endtest %}
