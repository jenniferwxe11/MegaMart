{% test discontinued_product_has_current_stockout_event(model) %}

with discontinued_products as (

    select
        product_id,
        discontinuation_date
    from {{ ref('product_lifecycles') }}
    where status = 'Discontinued'

),

invalid_products as (

    select
        d.product_id,
        d.discontinuation_date

    from discontinued_products d

    where not exists (

        select 1
        from {{ model }} s

        where s.product_id = d.product_id
          and s.stockout_start_date = d.discontinuation_date
          and s.stockout_end_date is null

    )

)

select *
from invalid_products

{% endtest %}
