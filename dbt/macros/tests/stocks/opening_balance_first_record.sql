{% test opening_balance_first_record(model) %}

with inventory_events as (

    select
        *,
        row_number() over (
            partition by store_id, product_id
            order by event_timestamp
        ) as rn

    from {{ model }}

)

select *

from inventory_events

where rn = 1
  and reason != 'Opening balance'

{% endtest %}
