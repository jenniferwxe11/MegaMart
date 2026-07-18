{% test customers_area_region_match(model, mapping_model) %}

select
    c.customer_id,
    c.region,
    c.area
from {{ model }} c
left join {{ mapping_model }} m
    on c.region = m.region
   and c.area = m.area
where
    c.region is not null
    and c.area is not null
    and m.area is null

{% endtest %}
