{% test current_product_content_quality_version_is_latest(model) %}

with ranked as (

    select
        product_id,
        content_version_id,
        valid_from,
        is_current,

        row_number() over (
            partition by product_id
            order by valid_from desc
        ) as version_rank

    from {{ model }}

)

select *
from ranked
where
    (version_rank = 1 and is_current != true)
    or
    (version_rank > 1 and is_current != false)

{% endtest %}
