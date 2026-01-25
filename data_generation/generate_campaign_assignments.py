import pandas as pd
from config import AUDIENCE_PERCENTAGE, CHANNEL_CONSENT_MAP, CONTROL_GROUP_PERCENTAGE

campaign_assignments = []

customers_df = pd.read_csv("data_generation/raw_data/customers_raw.csv")
customers_df.loc[:, "signup_date"] = pd.to_datetime(
    customers_df["signup_date"], errors="coerce"
)
# only choose customer types from online only and omnichannel
customers_df = customers_df[
    customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
]

campaigns_df = pd.read_csv("data_generation/raw_data/campaigns_raw.csv")
campaigns_df.loc[:, "start_date"] = pd.to_datetime(
    campaigns_df["start_date"], errors="coerce"
)
campaigns_df.loc[:, "is_ab_test"] = campaigns_df["is_ab_test"].astype(bool)

for _, campaign in campaigns_df.iterrows():
    consent_column = CHANNEL_CONSENT_MAP.get(campaign["channel"])
    eligible_customers = customers_df[
        (customers_df["signup_date"] <= campaign["start_date"])
        & (customers_df["customer_segment"] == campaign["target_segment"])
        & (customers_df[consent_column])
    ]

    target_audience_size = AUDIENCE_PERCENTAGE * len(eligible_customers)
    target_audience = eligible_customers.sample(n=target_audience_size, random_state=42)

    control_pct = CONTROL_GROUP_PERCENTAGE if campaign["is_ab_test"] else 0.0
    treatment_pct = (1.0 - CONTROL_GROUP_PERCENTAGE) if campaign["is_ab_test"] else 1.0
    treatment_size = int(treatment_pct * target_audience_size)
    treatment_customers = target_audience.sample(n=treatment_size, random_state=42)
    control_customers = target_audience.drop(treatment_customers.index)

    for _, customer in treatment_customers.iterrows():
        campaign_assignments.append(
            {
                "campaign_id": campaign["campaign_id"],
                "customer_id": customer["customer_id"],
                "group": "treatment",
                "assigned_at": campaign["start_date"],
            }
        )

    for _, customer in control_customers.iterrows():
        campaign_assignments.append(
            {
                "campaign_id": campaign["campaign_id"],
                "customer_id": customer["customer_id"],
                "group": "control",
                "assigned_at": campaign["start_date"],
            }
        )

df_campaign_assignments = pd.DataFrame(campaign_assignments)
df_campaign_assignments.to_csv(
    "data_generation/raw_data/campaign_assignments_raw.csv", index=False
)
print("campaign_assignments_raw.csv file generated")
