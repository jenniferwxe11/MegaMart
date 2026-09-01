{% test customer_has_required_campaign_consent(
    model,
    customer_model,
    campaign_model
) %}

with assignments as (

    select *
    from {{ model }}

),

customers as (

    select *
    from {{ customer_model }}

),

campaigns as (

    select *
    from {{ campaign_model }}

),

validation as (

    select
        a.campaign_id,
        a.customer_id,
        c.channels,
        cu.email_marketing_opt_in,
        cu.sms_marketing_opt_in,
        cu.push_notifications_opt_in

    from assignments a

    join campaigns c
        on a.campaign_id = c.campaign_id

    join customers cu
        on a.customer_id = cu.customer_id

)

select *

from validation

where

    (
        'Email' in unnest(channels)
        or 'SMS' in unnest(channels)
        or 'Push Notifications' in unnest(channels)
    )

    and not (

        (
            'Email' in unnest(channels)
            and email_marketing_opt_in
        )

        or

        (
            'SMS' in unnest(channels)
            and sms_marketing_opt_in
        )

        or

        (
            'Push Notifications' in unnest(channels)
            and push_notifications_opt_in
        )

    )

{% endtest %}
