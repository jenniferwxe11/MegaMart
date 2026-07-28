{% test opening_balance_delta_matches_stock_after(model) %}

select *

from {{ model }}

where reason = 'Opening balance'
  and delta != stock_after

{% endtest %}
