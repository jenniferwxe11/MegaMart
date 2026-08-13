{% test bundle_type_category_consistency(model, bundle_model, product_model) %}

with bundle_categories as (

    select
        bi.bundle_id,
        count(distinct p.category) as category_count

    from {{ model }} bi

    join {{ product_model }} p
        on bi.product_id = p.product_id

    group by bi.bundle_id

)

select
    b.bundle_id,
    b.bundle_type,
    bc.category_count

from {{ bundle_model }} b

join bundle_categories bc
    on b.bundle_id = bc.bundle_id

where
    b.bundle_type != 'Set'
    and bc.category_count > 1

{% endtest %}
