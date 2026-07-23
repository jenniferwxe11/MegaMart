{{ config(materialized='table') }}

select
    customer_id,
    customer_type,
    customer_name,
    email,
    gender,
    area,
    region,
    loyalty_points,
    customer_segment,
    email_marketing_opt_in,
    sms_marketing_opt_in,
    push_notifications_opt_in,
    device_category,
    device_platform,
    dob,
    signup_date
from {{ source('raw', 'customers') }}
