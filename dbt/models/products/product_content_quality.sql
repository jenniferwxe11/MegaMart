{{ config(materialized='table') }}

select
    content_version_id,
    product_id,
    quality_tier,
    has_image,
    image_count,
    image_quality_score,
    has_nutritional_info,
    has_description,
    description_length,
    missing_attribute_count,
    is_current,
    safe_cast(valid_from as date) as valid_from,
    safe_cast(valid_to as date) as valid_to
from {{ source('raw', 'product_content_quality') }}
