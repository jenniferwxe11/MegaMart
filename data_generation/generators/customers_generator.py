import random
from typing import Any

import pandas as pd

from data_generation.config.generation_config import NUM_CUSTOMERS
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.customers.customer_profile_service import (
    generate_customer_profile,
)
from data_generation.utils.io_utils import save


@register("customers_generator")
def customers_generator(ctx: GenerationContext):

    # ---------------------------
    # Storage
    # ---------------------------

    customers: list[dict[str, Any]] = []

    # ---------------------------
    # Generation
    # ---------------------------

    i = 1
    while len(customers) < NUM_CUSTOMERS:
        cid = f"CUST{i:03d}"
        customer_type = random.choices(
            ["Retail Walk-In", "Retail Members", "Online Only", "Omnichannel"],
            weights=[0.6, 0.15, 0.15, 0.1],
            k=1,
        )[0]

        # -----------------------------------------------------
        # CUSTOMER TYPE SEGMENTATION
        # Different customer types reflect varying levels of
        # data availability, engagement, and channel behaviour.
        # -----------------------------------------------------
        customer_profile = generate_customer_profile(ctx, customer_type)

        # Store Customer Record
        customers.append(
            {
                "customer_id": cid,
                "customer_type": customer_type,
                "customer_name": customer_profile["name"],
                "email": customer_profile["email"],
                "gender": customer_profile["gender"],
                "dob": customer_profile["dob"],
                "area": customer_profile["area"],
                "region": customer_profile["region"],
                "signup_date": customer_profile["signup_date"],
                "loyalty_points": customer_profile["loyalty_points"],
                "customer_segment": customer_profile["customer_segment"],
                "email_marketing_opt_in": customer_profile["email_marketing_opt_in"],
                "sms_marketing_opt_in": customer_profile["sms_marketing_opt_in"],
                "push_notifications_opt_in": customer_profile[
                    "push_notifications_opt_in"
                ],
                "device_category": customer_profile[
                    "device_category"
                ],  # mobile/desktop/tablet
                "device_platform": customer_profile[
                    "device_platform"
                ],  # IOS/andriod/web
            }
        )

        i += 1

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(customers), "customers_raw.csv")
