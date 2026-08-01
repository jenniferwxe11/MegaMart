{% test bundle_have_matching_promotion(model, promotion_model) %}

with bundle_events as (

    select
        cb.clickstream_id,
        cb.bundle_id,
        c.promotion_ids
    from (
        select *
        from {{ model }}
    ) cb
    inner join {{ ref('clickstreams') }} c
        on cb.clickstream_id = c.clickstream_id

),

expected_bundle_promotions as (

    select
        be.clickstream_id,
        be.bundle_id,
        p.promotion_id
    from bundle_events be
    cross join unnest(be.promotion_ids) as promotion_id
    inner join {{ promotion_model }} p
        on promotion_id = p.promotion_id
    where
        p.promotion_scope = 'Bundle'
        and p.promotion_target_id = be.bundle_id

)

select
    be.clickstream_id,
    be.bundle_id
from bundle_events be
left join expected_bundle_promotions ep
    on be.clickstream_id = ep.clickstream_id
    and be.bundle_id = ep.bundle_id
where ep.promotion_id is null

{% endtest %}
