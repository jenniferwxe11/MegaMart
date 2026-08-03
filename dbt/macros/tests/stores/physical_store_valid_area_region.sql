{% test physical_store_valid_area_region(model, area_region_model) %}

select
    s.store_id,
    s.store_type,
    s.region,
    s.area
from {{ model }} s
left join {{ area_region_model }} m
    on s.region = m.region
   and s.area = m.area
where
    s.store_type != 'Online'
    and s.region is not null
    and s.area is not null
    and m.area is null

{% endtest %}
