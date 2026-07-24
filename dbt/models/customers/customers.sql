{{ config(materialized='table') }}

select
    customer_id,
    customer_type,
    customer_name,
    email,
    gender,
    area,
    region,
    customer_segment,
    email_marketing_opt_in,
    sms_marketing_opt_in,
    push_notifications_opt_in,
    device_category,
    device_platform,
    safe_cast(dob as date) as dob,
    safe_cast(signup_date as date) as signup_date
from {{ source('raw', 'customers') }}
