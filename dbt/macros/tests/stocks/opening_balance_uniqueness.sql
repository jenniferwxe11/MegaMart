{% test opening_balance_uniqueness(model) %}

with opening_balances as (

    select
        store_id,
        product_id,
        count(*) as opening_balance_count

    from {{ model }}

    where reason = 'Opening balance'

    group by
        store_id,
        product_id

)

select *

from opening_balances

where opening_balance_count != 1

{% endtest %}
