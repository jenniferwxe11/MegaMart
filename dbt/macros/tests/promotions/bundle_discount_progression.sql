{% test bundle_discount_progression(model) %}

with ordered as (

    select
        bundle_id,
        pricing_phase,
        discount_value,

        lead(discount_value) over (
            partition by bundle_id
            order by
                case pricing_phase
                    when 'LAUNCH' then 1
                    when 'PROMO' then 2
                    when 'EOL' then 3
                end
        ) as next_discount_value

    from {{ model }}

)

select *

from ordered

where next_discount_value is not null
  and next_discount_value < discount_value

{% endtest %}
