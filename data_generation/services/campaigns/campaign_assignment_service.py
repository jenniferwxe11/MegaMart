import pandas as pd

from data_generation.config.campaigns_config import (
    CHANNEL_CONSENT_MAP,
    CONTROL_GROUP_PERCENTAGE,
    DIRECT_MESSAGE_CHANNELS,
    MIN_CONTROL_SIZE,
    MIN_TREATMENT_SIZE,
)


def apply_channel_filter(ctx, base_customers, channels):
    """
    Determines eligible customers for a campaign based on channel-specific rules.
    - Direct messaging channels (Email/SMS/Push Notifications) requires consent
    - Exposure only channels (Paid Advertisement/In-App) do not require consent
    """
    customers_df = ctx.customers.customers_df

    if any(channel in DIRECT_MESSAGE_CHANNELS for channel in channels):
        consent_columns = [
            CHANNEL_CONSENT_MAP.get(channel)
            for channel in channels
            if channel in DIRECT_MESSAGE_CHANNELS
        ]

        if consent_columns:
            return customers_df[customers_df[consent_columns].any(axis=1)]

    return base_customers


def assign_ab_groups(campaign, audience):
    """
    For A/B test campaigns, randomly assigns eligible customers to treatment and control groups.
    """
    if campaign["is_ab_test"]:
        # Split audience into treatment/control
        treatment = audience.sample(
            frac=(1 - CONTROL_GROUP_PERCENTAGE), random_state=42
        )
        control = audience.drop(treatment.index)

        # Ensure statistically meaningful group sizes
        if len(treatment) < MIN_TREATMENT_SIZE or len(control) < MIN_CONTROL_SIZE:
            # Fallback to full treatment if sample is too small
            campaign["is_ab_test"] = False
            treatment = audience
            control = pd.DataFrame()

    else:
        # Non experimental campaigns: all users receive treatment
        treatment = audience
        control = pd.DataFrame()
    return treatment, control
