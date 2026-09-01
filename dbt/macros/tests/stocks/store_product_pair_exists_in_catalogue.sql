{% test store_product_pair_exists_in_catalogue(model) %}

WITH invalid_snapshots AS (

    SELECT
        s.*

    FROM {{ model }} AS s

    LEFT JOIN {{ ref('store_catalogues') }} AS sc
        ON s.store_id = sc.store_id
       AND s.product_id = sc.product_id

    WHERE sc.store_id IS NULL

)

SELECT *
FROM invalid_snapshots

{% endtest %}
