# dirty_data_generation/generators/customers_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.customers_rules import (
    area_region_mismatch,
    duplicate_customer_id,
    duplicate_email,
    email_marketing_without_email,
    future_signup_date,
    invalid_customer_id_format,
    invalid_customer_name,
    invalid_customer_segment,
    invalid_customer_type,
    invalid_device_category,
    invalid_device_platform,
    invalid_dob,
    invalid_email_format,
    invalid_gender,
    missing_area,
    missing_customer_name,
    missing_customer_segment,
    missing_device_category,
    missing_dob,
    missing_email,
    missing_email_marketing_preference,
    missing_gender,
    missing_push_notifications_preference,
    missing_region,
    missing_sms_marketing_preference,
    push_notifications_without_device_platform,
    signup_before_dob,
    underage_customer,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

CUSTOMER_RULES = [
    # Missing Values
    (0.04, missing_customer_name),
    (0.04, missing_email),
    (0.03, missing_gender),
    (0.03, missing_dob),
    (0.03, missing_area),
    (0.03, missing_region),
    (0.03, missing_customer_segment),
    (0.03, missing_email_marketing_preference),
    (0.03, missing_sms_marketing_preference),
    (0.03, missing_push_notifications_preference),
    (0.03, missing_device_category),
    # Accepted Values
    (0.01, invalid_customer_type),
    (0.02, invalid_gender),
    (0.02, invalid_customer_segment),
    (0.02, invalid_device_platform),
    (0.02, invalid_device_category),
    # Formatting
    (0.02, invalid_customer_name),
    (0.03, invalid_email_format),
    (0.02, invalid_customer_id_format),
    # Duplicates
    (0.01, duplicate_customer_id),
    (0.03, duplicate_email),
    # Business Rule Violations
    (0.03, area_region_mismatch),
    (0.02, future_signup_date),
    (0.03, invalid_dob),
    (0.02, signup_before_dob),
    (0.02, underage_customer),
    (0.03, email_marketing_without_email),
    (0.03, push_notifications_without_device_platform),
]


@register("dirty_customers")
def dirty_customers(ctx: GenerationContext):

    df = ctx.customers.customers_df.copy()

    for rate, rule in CUSTOMER_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "customers_dirty.csv")
