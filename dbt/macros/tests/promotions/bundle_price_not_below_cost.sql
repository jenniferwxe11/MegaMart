{% test bundle_price_not_below_cost(model, bundle_items_model, product_model) %}

with bundle_costs as (

    select
        bi.bundle_id,
        sum(p.cost_price * bi.quantity) as total_cost

    from {{ bundle_items_model }} bi

    join {{ product_model }} p
        on bi.product_id = p.product_id

    group by bi.bundle_id

)

select
    bp.bundle_pricing_id,
    bp.bundle_id,
    bp.bundle_price,
    bc.total_cost

from {{ model }} bp

join bundle_costs bc
    on bp.bundle_id = bc.bundle_id

where bp.bundle_price < bc.total_cost

{% endtest %}
