{% test
    transaction_promotions_match_array(
        model,
        transaction_promotion_model
    )
%}






with promotion_arrays as (

    select
        transaction_id,
        array_agg(
            distinct promotion_id
            order by promotion_id
        ) as actual_promotions
    from {{ transaction_promotion_model }}
    group by transaction_id

)

select
    t.transaction_id,
    t.applied_promotions,
    pa.actual_promotions
from {{ model }} as t
left join promotion_arrays as pa
    on t.transaction_id = pa.transaction_id
where
    to_json_string(ifnull(t.applied_promotions, []))
    !=
    to_json_string(ifnull(pa.actual_promotions, []))






{% endtest %}
