{% test no_consecutive_duplicate_status(model) %}

with snapshots as (

    select
        *,
        lag(stock_band) over (
            partition by store_id, product_id
            order by week_start_date
        ) as previous_stock_band,

        lag(stock_status) over (
            partition by store_id, product_id
            order by week_start_date
        ) as previous_stock_status

    from {{ model }}

)

select *

from snapshots

where previous_stock_band is not null
  and stock_band = previous_stock_band
  and stock_status = previous_stock_status

{% endtest %}
