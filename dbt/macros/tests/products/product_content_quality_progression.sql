{% test product_content_quality_progression(model) %}

with ordered as (

    select
        product_id,
        content_version_id,
        valid_from,
        quality_tier,

        case quality_tier
            when 'Poor' then 1
            when 'Average' then 2
            when 'Good' then 3
            when 'Excellent' then 4
        end as tier_rank

    from {{ model }}

),

history as (

    select
        *,
        lag(tier_rank) over (
            partition by product_id
            order by valid_from
        ) as previous_rank

    from ordered

)

select *

from history

where previous_rank is not null
  and tier_rank < previous_rank

{% endtest %}
