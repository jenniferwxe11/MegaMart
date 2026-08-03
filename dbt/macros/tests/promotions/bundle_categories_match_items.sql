{% test bundle_categories_match_items(model, bundle_model, product_model) %}

with expected as (

    select
        bi.bundle_id,
        array_agg(distinct p.category order by p.category) as expected_categories
    from {{ model }} bi
    join {{ product_model }} p
      on bi.product_id = p.product_id
    group by bi.bundle_id

)

select
    b.bundle_id,
    b.categories,
    e.expected_categories
from {{ bundle_model }} b
join expected e
  on b.bundle_id = e.bundle_id
where b.categories is not null
  and to_json_string(b.categories)
      != to_json_string(e.expected_categories)

{% endtest %}
