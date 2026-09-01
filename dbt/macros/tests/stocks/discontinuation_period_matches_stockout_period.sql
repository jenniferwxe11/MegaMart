{% test discontinuation_period_matches_stockout_period(model) %}

with discontinued_products as (

    select
        product_id,
        discontinuation_date
    from {{ ref('product_lifecycles') }}
    where status = 'Discontinued'

),

matching_stockouts as (

    select
        d.product_id,
        d.discontinuation_date,
        s.store_id,
        s.stockout_start_date

    from discontinued_products d

    left join {{ model }} s
        on d.product_id = s.product_id
       and s.stockout_start_date = d.discontinuation_date

)

select *

from matching_stockouts

where stockout_start_date is null

{% endtest %}
