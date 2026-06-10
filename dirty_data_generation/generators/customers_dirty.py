import random
from datetime import datetime

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
    append_error(df, indices, "duplicate email")

    # Mixed-case/whitespace in email
    df = inject_whitespace(
        df, col="email", rate=0.08, error_label="email formatting anomaly"
    )

    # Future signup dates
    future_indices = df.sample(frac=0.02, random_state=2).index
    df.loc[future_indices, "signup_date"] = [
        fake.future_datetime(end_date="+10y") for _ in range(len(future_indices))
    ]
    append_error(df, future_indices, "future signup date")

    # DOB in the future or impossibly old
    dob_indices = df[df["dob"].notna()].sample(frac=0.03, random_state=3).index
    df.loc[dob_indices, "dob"] = [
        random.choice(
            [
                fake.future_datetime(end_date="+10y"),  # future
                fake.past_datetime(start_date=datetime(1800, 1, 1)),  # impossibly old
            ]
        )
        for _ in range(len(dob_indices))
    ]
    append_error(df, dob_indices, "invalid date of birth")

    # Age < 18 (DOB too recent)
    young_indices = df[df["dob"].notna()].sample(frac=0.02, random_state=4).index
    df.loc[young_indices, "dob"] = pd.to_datetime(
        [
            fake.date_between(start_date="-12y", end_date="-5y")
            for _ in range(len(young_indices))
        ]
    )
    append_error(df, young_indices, "underage date of birth")

    # Loyalty points negative
    neg_idx = (
        df[df["loyalty_points"].notna() & (df["loyalty_points"] < 0)]
        .sample(frac=0.02, random_state=5)
        .index
    )
    df.loc[neg_idx, "loyalty_points"] = [
        -random.randint(1, 500) for _ in range(len(neg_idx))
    ]
    append_error(df, neg_idx, "negative loyalty points")

    # Invalid gender values
    gender_indices = df[df["gender"].notna()].sample(frac=0.01, random_state=6).index
    df.loc[gender_indices, "gender"] = [
        random.choice(["f", "m", "male", "female", "unknown", ""])
        for _ in range(len(gender_indices))
    ]
    append_error(df, gender_indices, "invalid gender value")

    # Missing customer_segment for non-walk-in
    df = inject_nulls(
        df,
        online_mask,
        "customer_segment",
        rate=0.04,
        error_label="missing customer segment",
    )

    # Opt-in flag stored as string instead of bool
    for col in [
        "email_marketing_opt_in",
        "sms_marketing_opt_in",
        "push_notifications_opt_in",
    ]:
        str_mask = df[col].notna() & pd.Series(
            [random.random() < 0.05 for _ in range(len(df))], index=df.index
        )

        affected_indices = df[str_mask].index

        df.loc[str_mask, col] = df.loc[str_mask, col].map(
            {True: "true", False: "false", "true": "true", "false": "false"}
        )

        append_error(df, affected_indices, f"{col} stored as string")

    # Whitespace in customer_name
    df = inject_whitespace(
        df,
        col="customer_name",
        rate=0.05,
        error_label="customer name formatting anomaly",
    )

    return save(df, "customers_dirty.csv")
