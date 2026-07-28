{% test snapshot_period_within_product_lifecycle(model) %}

WITH invalid_snapshots AS (

    SELECT
        s.*

    FROM {{ model }} AS s

    LEFT JOIN {{ ref('product_lifecycles') }} AS pl
        ON s.product_id = pl.product_id
       AND s.week_start_date >= pl.valid_from
       AND (
            pl.valid_to IS NULL
            OR s.week_start_date <= pl.valid_to
       )

    WHERE pl.product_id IS NULL

)

SELECT *
FROM invalid_snapshots

{% endtest %}
