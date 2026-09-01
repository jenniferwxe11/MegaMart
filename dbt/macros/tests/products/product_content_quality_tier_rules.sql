{% test product_content_quality_tier_rules(model) %}

select *
from {{ model }}
where

-- Poor
(
    quality_tier = 'Poor'
    and (
        image_count > 1
        or image_quality_score > 0.40
        or description_length > 50
    )
)

or

-- Average
(
    quality_tier = 'Average'
    and (
        image_count < 1
        or image_count > 3
        or image_quality_score < 0.40
        or image_quality_score > 0.70
        or description_length < 50
        or description_length > 120
    )
)

or

-- Good
(
    quality_tier = 'Good'
    and (
        image_count < 3
        or image_count > 5
        or image_quality_score < 0.70
        or image_quality_score > 0.90
        or description_length < 120
        or description_length > 250
    )
)

or

-- Excellent
(
    quality_tier = 'Excellent'
    and (
        image_count < 5
        or image_quality_score < 0.90
        or missing_attribute_count <> 0
        or description_length < 250
    )
)

{% endtest %}
