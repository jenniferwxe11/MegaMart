from typing import Any

import pandas as pd

from data_generation.config.campaigns_config import AUDIENCE_PERCENTAGE
from data_generation.config.generation_config import (
    LIMIT_CAMPAIGN_ASSIGNMENTS,
    LIMIT_CAMPAIGN_EXPOSURES,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.campaigns.campaign_assignment_service import (
    apply_channel_filter,
    assign_ab_groups,
)
from data_generation.services.campaigns.campaign_exposure_service import (
    simulate_exposure,
)
from data_generation.utils.io_utils import save


@register("campaign_assignments_generator")
def campaign_assignments_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    customers_df = ctx.customers.customers_df
    # Assumption: Only able to track campaign response for customers with digital activity
    customers_df = customers_df[
        customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
    ].copy()

    assert ctx.campaigns is not None
    campaigns_df = ctx.campaigns.campaigns_df

    # ---------------------------
    # Storage
    # ---------------------------

    campaign_assignments: list[dict[str, Any]] = []
    campaign_exposures: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    for _, campaign in campaigns_df.iterrows():

        if (
            len(campaign_assignments) >= LIMIT_CAMPAIGN_ASSIGNMENTS
            and len(campaign_exposures) >= LIMIT_CAMPAIGN_EXPOSURES
        ):
            break

        base_customers = customers_df[
            (customers_df["signup_date"] <= campaign["start_date"])
            & (customers_df["customer_segment"] == campaign["target_segment"])
        ]

        # --- Apply channel consent filter ---
        channels = campaign["channels"]
        eligible_customers = apply_channel_filter(ctx, base_customers, channels)

        # Skip campaign assignment if no eligible customers
        if eligible_customers.empty:
            continue

        # Sample campaign audience from eligible customers
        audience = eligible_customers.sample(frac=AUDIENCE_PERCENTAGE, random_state=42)

        # --- A/B Test Assignment ---
        treatment, control = assign_ab_groups(campaign, audience)

        # Store Campaign Assigment Record
        for _, customer in treatment.iterrows():
            campaign_assignments.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "customer_id": customer["customer_id"],
                    "group": "Treatment",
                    "eligible_at": campaign["start_date"],
                }
            )

        for _, customer in control.iterrows():
            campaign_assignments.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "customer_id": customer["customer_id"],
                    "group": "Control",
                    "eligible_at": campaign["start_date"],
                }
            )

        for channel in channels:
            # --- Campaign Exposure Generation ---
            for _, customer in audience.iterrows():
                customer_id = customer["customer_id"]
                campaign_id = campaign["campaign_id"]

                # Identify campaign group
                treatment_ids = set(treatment["customer_id"])
                group = "Treatment" if customer_id in treatment_ids else "Control"

                eligible = True

                # --- Simulate Engagement for Treatment Group ---
                exposure = simulate_exposure(customer, campaign, channel, group)

                # Store Campaign Exposure Record
                campaign_exposures.append(
                    {
                        "customer_id": customer_id,
                        "campaign_id": campaign_id,
                        "channel": channel,
                        "group": group,
                        "eligible": eligible,
                        "exposed": exposure["exposed"],
                        "exposed_time": exposure["exposed_time"],
                        "opened": exposure["opened"],
                        "opened_time": exposure["opened_time"],
                        "clicked": exposure["clicked"],
                        "clicked_time": exposure["clicked_time"],
                        "device_platform": exposure["device_platform"],
                        "cost_per_msg": exposure["cost_per_msg"],
                    }
                )

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(campaign_assignments), "campaign_assignments_raw.csv")
    save(pd.DataFrame(campaign_exposures), "campaign_exposures_raw.csv")
