{% test bundle_pricing_progression(model) %}

with ordered as (

    select
        bundle_id,
        pricing_phase,
        bundle_price,

        lead(bundle_price) over (
            partition by bundle_id
            order by
                case pricing_phase
                    when 'LAUNCH' then 1
                    when 'PROMO' then 2
                    when 'EOL' then 3
                end
        ) as next_bundle_price

    from {{ model }}

)

select *

from ordered

where next_bundle_price is not null
  and next_bundle_price > bundle_price

{% endtest %}
