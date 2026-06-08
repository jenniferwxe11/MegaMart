import random
from datetime import timedelta
from typing import Any

import pandas as pd
from faker import Faker

from data_generation.config.campaigns_config import (
    ADDITIONAL_CAMPAIGN_RULES,
    ADJECTIVES,
    CAMPAIGN_NAME_SUFFIXES,
    CAMPAIGN_TYPE_DISTRIBUTION,
    CAMPAIGN_TYPE_NAMING,
    PRIMARY_SEGMENT_BY_CAMPAIGN,
)
from data_generation.config.constants import SEASONAL_DATES
from data_generation.config.generation_config import NUM_CAMPAIGNS
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.campaigns.campaign_service import (
    calculate_budget,
    pick_channels,
)
from data_generation.utils.io_utils import save

fake = Faker()


@register("campaigns_generator")
def campaigns_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    DATA_START_DATE = ctx.config.DATA_START_DATE
    DATA_END_DATE = ctx.config.DATA_END_DATE

    # ---------------------------
    # Storage
    # ---------------------------

    campaigns: list[dict[str, Any]] = []

    # --------------------------------------------------
    # SEASONAL CAMPAIGN GENERATION
    # Purpose: Model campaigns tied to key retail events
    # (e.g. Commercial Mega Sales, Cultural Festivals)
    # --------------------------------------------------

    i = 1
    campaign_type = "Seasonal"
    for season_type, events in SEASONAL_DATES.items():

        if len(campaigns) >= NUM_CAMPAIGNS:
            break

        for event_name, dates in events.items():
            season = event_name
            for event_date in dates:

                # Define campaign window based on event type
                offset: int = random.choice(
                    ADDITIONAL_CAMPAIGN_RULES[campaign_type]["duration_days"]
                )
                if season_type == "Commercial Mega Sale":
                    start_date = event_date - timedelta(days=offset)
                    end_date = event_date
                elif season_type == "Cultural Festival":
                    start_date = event_date - timedelta(days=offset)
                    end_date = event_date + timedelta(days=offset)

                campaign_id = f"CAMP{i:03d}"

                # Assign primary customer segment based on campagin strategy
                target_segment = random.choices(
                    list(PRIMARY_SEGMENT_BY_CAMPAIGN[campaign_type].keys()),
                    weights=list(PRIMARY_SEGMENT_BY_CAMPAIGN[campaign_type].values()),
                    k=1,
                )[0]

                channels = pick_channels(campaign_type)

                # Allocate total campaign budget across selected channels
                budget = calculate_budget(channels, campaign_type)

                # Decide if campaign includes A/B testing
                is_ab_test = (
                    random.random()
                    < ADDITIONAL_CAMPAIGN_RULES[campaign_type]["ab_test_prob"]
                )

                # Generate campaign name
                adjective = random.choice(ADJECTIVES)
                last_word = random.choice(CAMPAIGN_NAME_SUFFIXES)
                campaign_name = f"MegaMart {event_name} {adjective} {last_word}"

                # Assumption: All campaigns are completed (historical dataset)
                status = "Completed"

                # Store Seasonal Campaign Record
                campaigns.append(
                    {
                        "campaign_id": campaign_id,
                        "campaign_name": campaign_name,
                        "campaign_type": campaign_type,
                        "target_segment": target_segment,
                        "season": season,
                        "channels": channels,
                        "start_date": start_date,
                        "end_date": end_date,
                        "budget": budget,
                        "is_ab_test": is_ab_test,
                        "status": status,
                    }
                )
                i += 1

    # --------------------------------------------------
    # ALWAYS ON CAMPAIGN GENERATION
    # Types: Acquisition, Retention, Clearance
    # Purpose: Simulate non-seasonal marketing activity
    # --------------------------------------------------

    while len(campaigns) < NUM_CAMPAIGNS:
        campaign_id = f"CAMP{i:03d}"
        campaign_type = random.choices(
            list(CAMPAIGN_TYPE_DISTRIBUTION.keys()),
            weights=list(CAMPAIGN_TYPE_DISTRIBUTION.values()),
            k=1,
        )[0]

        # Assign target segment based on campaign type probabilities
        target_segment = random.choices(
            list(PRIMARY_SEGMENT_BY_CAMPAIGN[campaign_type].keys()),
            weights=list(PRIMARY_SEGMENT_BY_CAMPAIGN[campaign_type].values()),
            k=1,
        )[0]

        channels = pick_channels(campaign_type)

        # Assign campaign duration within operational timeframe
        start_date = pd.to_datetime(
            fake.date_time_between(
                start_date=pd.Timestamp(DATA_START_DATE).to_pydatetime(),
                end_date=(
                    pd.Timestamp(DATA_END_DATE) - timedelta(weeks=1)
                ).to_pydatetime(),
            )
        )
        duration_min, duration_max = ADDITIONAL_CAMPAIGN_RULES[campaign_type][
            "duration_days"
        ]
        duration_days = random.randint(duration_min, duration_max)
        end_date = start_date + timedelta(days=duration_days)

        budget = calculate_budget(channels, campaign_type)

        is_ab_test = (
            random.random() < ADDITIONAL_CAMPAIGN_RULES[campaign_type]["ab_test_prob"]
        )

        # Generate campaign name using type specific naming branding conventions
        first_word = random.choice(CAMPAIGN_TYPE_NAMING[campaign_type])
        adjective = random.choice(ADJECTIVES)
        last_word = random.choice(CAMPAIGN_NAME_SUFFIXES)
        campaign_name = f"MegaMart {first_word} {adjective} {last_word}"

        # Assumption: All campaigns are completed (historical dataset)
        status = "Completed"

        # Store Always On Campaign Record
        campaigns.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "campaign_type": campaign_type,
                "target_segment": target_segment,
                "season": None,
                "channels": channels,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
                "is_ab_test": is_ab_test,
                "status": status,
            }
        )
        i += 1

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(campaigns), "campaigns_raw.csv")
