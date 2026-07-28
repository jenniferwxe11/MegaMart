{% test delta_matches_stock_after_movement(model) %}

with inventory_events as (

    select
        *,
        lag(stock_after) over (
            partition by store_id, product_id
            order by event_timestamp
        ) as previous_stock_after

    from {{ model }}

)

select *

from inventory_events

where previous_stock_after is not null
  and delta != stock_after - previous_stock_after

{% endtest %}
