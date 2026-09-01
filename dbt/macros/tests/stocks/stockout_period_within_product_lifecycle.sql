{% test stockout_period_within_product_lifecycle(model) %}

with stockouts as (

    select *
    from {{ model }}

),

product_lifecycles as (

    select *
    from {{ ref('product_lifecycles') }}

),

invalid_stockouts as (

    select
        s.*

    from stockouts s

    left join product_lifecycles pl
        on s.product_id = pl.product_id
        and s.stockout_start_date >= pl.valid_from
        and s.stockout_start_date <= coalesce(pl.valid_to, current_date())

    where pl.product_id is null

)

select *
from invalid_stockouts

{% endtest %}
