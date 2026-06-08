import random
from datetime import timedelta

import numpy as np

from data_generation.config.campaigns_config import (
    COST_PER_MSG,
    DIRECT_MESSAGE_CHANNEL_RATE,
    DIRECT_MESSAGE_CHANNELS,
    EXPOSURE_ONLY_CHANNEL_RATES,
    EXPOSURE_ONLY_CHANNELS,
)


def simulate_exposure(customer, campaign, channel, group):
    """
    Simulate whether a customer is exposed to the campaign based on channel and group assignment.
    """
    exposed = False
    exposed_time = None
    opened = False
    opened_time = None
    clicked = False
    clicked_time = None
    cost_per_msg = 0.0
    device_platform = customer["device_platform"]

    if group == "Treatment":
        # Channel specific delivery probability
        if channel in DIRECT_MESSAGE_CHANNELS:
            exposed = random.random() < DIRECT_MESSAGE_CHANNEL_RATE["Deliver"].get(
                channel, 1.0
            )
        elif channel in EXPOSURE_ONLY_CHANNELS:
            exposed = random.random() < EXPOSURE_ONLY_CHANNEL_RATES["Deliver"].get(
                channel, 1.0
            )

        if exposed:
            # Cost incurred only upon successful delivery
            cost_per_msg = COST_PER_MSG.get(channel, 0.0)

            # Bias exposure timing toward earlier campaign period
            campaign_duration = (
                campaign["end_date"] - campaign["start_date"]
            ).total_seconds()
            skew_factor = np.random.beta(a=2, b=5)
            delta_seconds = int(skew_factor * campaign_duration)
            exposed_time = min(
                campaign["start_date"] + timedelta(seconds=delta_seconds),
                campaign["end_date"],
            )

            # ---------------------------------------------------------
            # Simulate Engagement by Channel Type
            # ---------------------------------------------------------

            if channel in DIRECT_MESSAGE_CHANNELS:
                # Direct channels follow funnel: delivery → open → click
                opened = random.random() < DIRECT_MESSAGE_CHANNEL_RATE["Open"].get(
                    channel, 1.0
                )
                if opened:
                    max_open = int(
                        (campaign["end_date"] - exposed_time).total_seconds()
                    )
                    delta_open = random.randint(10, min(max_open, 3600))
                    opened_time = exposed_time + timedelta(seconds=delta_open)

                    clicked = random.random() < DIRECT_MESSAGE_CHANNEL_RATE[
                        "Click"
                    ].get(channel, 1.0)
                    if clicked:
                        max_click = int(
                            (campaign["end_date"] - opened_time).total_seconds()
                        )
                        delta_click = random.randint(5, min(max_click, 300))
                        clicked_time = opened_time + timedelta(seconds=delta_click)

            elif channel in EXPOSURE_ONLY_CHANNELS:
                # Exposure channels: no open event, clicks occur directly from impression
                clicked = random.random() < EXPOSURE_ONLY_CHANNEL_RATES["Click"].get(
                    channel, 1.0
                )
                if clicked:
                    max_click = int(
                        (campaign["end_date"] - exposed_time).total_seconds()
                    )
                    delta_click = random.randint(5, min(max_click, 300))
                    clicked_time = exposed_time + timedelta(seconds=delta_click)

    exposure = {
        "exposed": exposed,
        "exposed_time": exposed_time,
        "opened": opened,
        "opened_time": opened_time,
        "clicked": clicked,
        "clicked_time": clicked_time,
        "device_platform": device_platform,
        "cost_per_msg": cost_per_msg,
    }

    return exposure
