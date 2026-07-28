{% test non_overlapping_stockout_windows(model) %}

with stockouts as (

    select
        store_id,
        product_id,
        stockout_start_date,
        stockout_end_date,
        lag(stockout_end_date) over (
            partition by store_id, product_id
            order by stockout_start_date
        ) as previous_end_date

    from {{ model }}

)

select *

from stockouts

where previous_end_date is not null
  and stockout_start_date <= previous_end_date

{% endtest %}
