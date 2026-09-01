{% test customer_segment_matches_customer_table(model, customer_model) %}

select
    c.clickstream_id,
    c.customer_id,
    c.customer_segment as clickstream_customer_segment,
    cu.customer_segment as customer_table_customer_segment
from {{ model }} c
inner join {{ customer_model }} cu
    on c.customer_id = cu.customer_id
where c.customer_segment != cu.customer_segment

{% endtest %}
