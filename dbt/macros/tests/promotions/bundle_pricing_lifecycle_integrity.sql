{% test bundle_pricing_lifecycle_integrity(model) %}

WITH pricing_phases AS (

    SELECT
        bundle_id,
        pricing_phase,
        effective_start_date,
        effective_end_date,

        CASE pricing_phase
            WHEN 'LAUNCH' THEN 1
            WHEN 'PROMO' THEN 2
            WHEN 'EOL' THEN 3
        END AS phase_order

    FROM {{ model }}

),

ordered AS (

    SELECT
        *,

        LEAD(effective_start_date) OVER (
            PARTITION BY bundle_id
            ORDER BY phase_order
        ) AS next_start_date,

        LEAD(phase_order) OVER (
            PARTITION BY bundle_id
            ORDER BY phase_order
        ) AS next_phase_order

    FROM pricing_phases

)

SELECT *

FROM ordered

WHERE

    ------------------------------------------------------------------
    -- Invalid individual phase
    ------------------------------------------------------------------
    effective_start_date > effective_end_date

    ------------------------------------------------------------------
    -- Phases appear in the wrong order
    ------------------------------------------------------------------
    OR (
        next_phase_order IS NOT NULL
        AND next_phase_order <= phase_order
    )

    ------------------------------------------------------------------
    -- Overlapping phases
    ------------------------------------------------------------------
    OR (
        next_start_date IS NOT NULL
        AND next_start_date <= effective_end_date
    )

    ------------------------------------------------------------------
    -- Gaps between consecutive phases
    ------------------------------------------------------------------
    OR (
        next_start_date IS NOT NULL
        AND DATE_DIFF(next_start_date, effective_end_date, DAY) > 1
    )

{% endtest %}
