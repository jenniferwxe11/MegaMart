{% test bundle_promotions_match_bundle_pricing(model, promotion_model) %}

with latest_bundle_price as (

    select
        bundle_id,
        discount_value,
        row_number() over (
            partition by bundle_id
            order by effective_end_date desc,
                     effective_start_date desc
        ) as rn
    from {{ model }}

)

select
    p.promotion_id,
    p.promotion_target_id,
    p.promotion_value,
    bp.discount_value
from {{ promotion_model }} p
join latest_bundle_price bp
  on p.promotion_target_id = bp.bundle_id
 and bp.rn = 1
where p.promotion_mechanic = 'bundle'
  and (
        p.promotion_scope <> 'bundle'
        or round(p.promotion_value,2) <> round(bp.discount_value,2)
      )

{% endtest %}
