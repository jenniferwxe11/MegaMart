{% test no_duplicate_category_inside_categories(model) %}

select
    bundle_id,
    categories
from {{ model }}
where categories is not null
  and array_length(categories) != (
        select count(distinct category)
        from unnest(categories) as category
    )

{% endtest %}
