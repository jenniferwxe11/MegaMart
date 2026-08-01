{% test bundle_referenced_must_belong_to_promotion(model, promotion_model) %}

with clickstream_bundles as (

    select
        clickstream_id,
        bundle_id,
        promotion_ids

    from {{ model }}

    cross join unnest(bundle_ids) as bundle_id

),

promotion_targets as (

    select
        cb.clickstream_id,
        cb.bundle_id,
        p.promotion_target_id

    from clickstream_bundles cb

    cross join unnest(cb.promotion_ids) as promotion_id

    inner join {{ promotion_model }} p
        on promotion_id = p.promotion_id

    where p.promotion_scope = 'bundle'

)

select
    cb.clickstream_id,
    cb.bundle_id

from clickstream_bundles cb

left join promotion_targets pt
    on cb.clickstream_id = pt.clickstream_id
    and cb.bundle_id = pt.promotion_target_id

where pt.promotion_target_id is null

{% endtest %}
