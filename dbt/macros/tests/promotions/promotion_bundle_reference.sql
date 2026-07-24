{% test promotion_bundle_reference(model) %}

SELECT
    p.promotion_id,
    p.promotion_target_id
FROM {{ model }} AS p

LEFT JOIN {{ ref('bundles') }} AS b
    ON p.promotion_target_id = b.bundle_id

WHERE
    p.promotion_scope = 'bundle'
    AND b.bundle_id IS NULL

{% endtest %}
