import pandas as pd

from data_generation.config.campaigns_config import (
    CHANNEL_CONSENT_MAP,
    CONTROL_GROUP_PERCENTAGE,
    DIRECT_MESSAGE_CHANNELS,
)
from data_generation.config.generation_config import (
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
    if not campaign["is_ab_test"]:
        return audience, pd.DataFrame()

    if len(audience) < (MIN_TREATMENT_SIZE + MIN_CONTROL_SIZE):
        empty = audience.iloc[0:0].copy()
        return empty, empty

    seed = hash(campaign["campaign_id"]) % 2**32

    treatment = audience.sample(frac=(1 - CONTROL_GROUP_PERCENTAGE), random_state=seed)
    control = audience.drop(treatment.index)

    return treatment, control
