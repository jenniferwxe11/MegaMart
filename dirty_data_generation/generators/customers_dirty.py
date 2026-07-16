import random
from datetime import date

import pandas as pd
from faker import Faker

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.dirty_helpers import (
    append_error,
    inject_nulls,
    inject_whitespace,
)
from dirty_data_generation.utils.io_utils import save

fake = Faker()


@register("dirty_customers")
def dirty_customers(ctx: GenerationContext):
    df = ctx.customers.customers_df.copy()

    df["error_types"] = [[] for _ in range(len(df))]

    # Missing name/email for non-walk-in customers
    online_mask = df["customer_type"].isin(["Online Only", "Omnichannel"])
    for col in ["customer_name", "email", "gender", "age", "region", "area"]:
        df = inject_nulls(df, online_mask, col, rate=0.06, error_label=f"missing {col}")

    # Duplicate emails
    email_pool = df["email"].dropna().tolist()
    dup_mask = online_mask & df["email"].notna()
    indices = df[dup_mask].sample(frac=0.03, random_state=1).index
    df.loc[indices, "email"] = [random.choice(email_pool) for _ in range(len(indices))]
    append_error(
        df,
        indices,
        error_label="duplicate email",
        columns=["email"],
    )

    # Mixed-case/whitespace in email
    df = inject_whitespace(
        df, col="email", rate=0.08, error_label="email formatting anomaly"
    )

    # Area-region mismatch
    area_region_map = ctx.region_areas.area_region_map
    regions = ctx.region_areas.regions

    mismatch_idx = (
        df[df["area"].notna() & df["region"].notna()]
        .sample(frac=0.03, random_state=9)
        .index
    )

    for idx in mismatch_idx:
        area = df.at[idx, "area"]

        correct_region = area_region_map.get(area)

        if correct_region is None:
            continue

        df.at[idx, "region"] = random.choice(
            [r for r in regions if r != correct_region]
        )

    append_error(
        df,
        mismatch_idx,
        error_label="area-region mismatch",
        columns=["area", "region"],
    )

    # Future signup dates
    future_indices = df.sample(frac=0.02, random_state=2).index
    df.loc[future_indices, "signup_date"] = pd.to_datetime(
        [fake.future_date(end_date="+10y") for _ in range(len(future_indices))]
    )
    append_error(
        df,
        future_indices,
        error_label="future signup date",
        columns=["signup_date"],
    )

    # DOB in the future or impossibly old
    dob_indices = df[df["dob"].notna()].sample(frac=0.03, random_state=3).index
    df.loc[dob_indices, "dob"] = pd.to_datetime(
        [
            random.choice(
                [
                    fake.future_date(end_date="+10y"),  # future
                    fake.past_date(start_date=date(1800, 1, 1)),  # impossibly old
                ]
            )
            for _ in range(len(dob_indices))
        ]
    )
    append_error(
        df,
        dob_indices,
        error_label="invalid date of birth",
        columns=["dob"],
    )

    # Age < 18 (DOB too recent)
    young_indices = df[df["dob"].notna()].sample(frac=0.02, random_state=4).index
    df.loc[young_indices, "dob"] = pd.to_datetime(
        [
            fake.date_between(start_date="-12y", end_date="-5y")
            for _ in range(len(young_indices))
        ]
    )
    append_error(
        df,
        young_indices,
        error_label="underage date of birth",
        columns=["dob"],
    )

    # Loyalty points negative
    neg_idx = (
        df[df["loyalty_points"].notna() & (df["loyalty_points"] < 0)]
        .sample(frac=0.02, random_state=5)
        .index
    )
    df.loc[neg_idx, "loyalty_points"] = [
        -random.randint(1, 500) for _ in range(len(neg_idx))
    ]
    append_error(
        df,
        neg_idx,
        error_label="negative loyalty points",
        columns=["loyalty_points"],
    )

    # Invalid gender values
    gender_indices = df[df["gender"].notna()].sample(frac=0.01, random_state=6).index
    df.loc[gender_indices, "gender"] = [
        random.choice(["f", "m", "male", "female", "unknown", ""])
        for _ in range(len(gender_indices))
    ]
    append_error(
        df,
        gender_indices,
        error_label="invalid gender value",
        columns=["gender"],
    )

    # Missing customer_segment for non-walk-in
    df = inject_nulls(
        df,
        online_mask,
        "customer_segment",
        rate=0.04,
        error_label="missing customer segment",
    )

    # Missing marketing preferences
    for col in [
        "email_marketing_opt_in",
        "sms_marketing_opt_in",
        "push_notifications_opt_in",
    ]:
        df = inject_nulls(
            df,
            df[col].notna(),
            col,
            rate=0.03,
            error_label=f"missing {col}",
        )

    # Email marketing enabled but email missing
    email_idx = df[df["email"].notna()].sample(frac=0.03, random_state=7).index

    df.loc[email_idx, "email"] = None
    df.loc[email_idx, "email_marketing_opt_in"] = True
    append_error(
        df,
        email_idx,
        error_label="email marketing enabled without email",
        columns=["email", "email_marketing_opt_in"],
    )

    # Push notifications enabled but device platform missing
    push_idx = df[df["device_platform"].notna()].sample(frac=0.03, random_state=8).index

    df.loc[push_idx, "device_platform"] = None
    df.loc[push_idx, "push_notifications_opt_in"] = True
    append_error(
        df,
        push_idx,
        error_label="push notifications enabled without device platform",
        columns=["device_platform", "push_notifications_opt_in"],
    )

    # Whitespace in customer_name
    df = inject_whitespace(
        df,
        col="customer_name",
        rate=0.05,
        error_label="customer name formatting anomaly",
    )

    # Device category missing if device platform is present
    device_idx = (
        df[df["device_platform"].notna()].sample(frac=0.03, random_state=9).index
    )

    df.loc[device_idx, "device_category"] = None

    append_error(
        df,
        device_idx,
        error_label="device category missing for device platform",
        columns=["device_platform", "device_category"],
    )

    return save(df, "customers_dirty.csv")
