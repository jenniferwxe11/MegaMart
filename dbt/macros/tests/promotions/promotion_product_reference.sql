{% test promotion_product_reference(model) %}

SELECT
    p.promotion_id,
    p.promotion_target_id
FROM {{ model }} AS p

LEFT JOIN {{ ref('products') }} AS pr
    ON p.promotion_target_id = pr.product_id

WHERE
    p.promotion_scope = 'product'
    AND pr.product_id IS NULL

{% endtest %}
