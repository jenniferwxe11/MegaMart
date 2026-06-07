import random

from data_generation.config.campaigns_config import (
    BUDGET_MULTIPLIER_BY_CAMPAIGN,
    BUDGET_RANGES_BY_CHANNEL,
    CHANNEL_PROB_BY_CAMPAIGN,
    MAX_CHANNELS_PER_CAMPAIGN_TYPE,
)


def pick_channels(campaign_type):
    """
    Selects marketing channels based on campaign type strategy.

    Purpose:
    - Reflect channel mix differences (e.g. acquisition vs retention)
    - Simulate realistic multi-channel campaign execution
    """
    max_channels = MAX_CHANNELS_PER_CAMPAIGN_TYPE.get(campaign_type, 1)
    num_channels = random.randint(1, max_channels)
    channels = random.choices(
        list(CHANNEL_PROB_BY_CAMPAIGN[campaign_type].keys()),
        weights=list(CHANNEL_PROB_BY_CAMPAIGN[campaign_type].values()),
        k=num_channels * 3,
    )
    channels = list(dict.fromkeys(channels))[:num_channels]
    return channels


def calculate_budget(channels, campaign_type):
    """
    Estimates total campaign budget across selected channels.

    Purpose:
    - Simulate realistic marketing spend allocation
    """
    total_budget = 0
    for channel in channels:
        base_min, base_max = BUDGET_RANGES_BY_CHANNEL[channel]
        multiplier = BUDGET_MULTIPLIER_BY_CAMPAIGN[campaign_type]
        channel_budget = round(
            random.randint(
                int(base_min * multiplier),
                int(base_max * multiplier),
            ),
            -2,
        )
        total_budget += channel_budget
    return round(total_budget, 2)
