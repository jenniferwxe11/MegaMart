import random

import numpy as np
import pandas as pd
import pytest

from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_location,
)
from data_generation.services.clickstreams.clickstream_session_service import (
    attempt_reactivation,
    decide_next_activity,
)
from tests.helpers import _build_customer_with_location

# ============================================================
# get_location()
# ============================================================
# Integration contract: uses customer data


def test_clickstream_session_flow_get_location_home_area(ctx):
    """
    Integration contract: get_location() must return the customer's
    home area ~80% of the time.
    """
    customer = _build_customer_with_location(ctx)
    customer_id = customer["customer_id"]
    cust_area = customer["area"]
    hits, trials = 0, 100
    for _ in range(trials):
        result = get_location(ctx, customer_id)
        if result == cust_area:
            hits += 1
    ratio = hits / trials
    assert 0.7 <= ratio <= 0.9, (
        f"Expected home area probability 0.7-0.9, got {ratio:.2f} "
        f"for customer {customer_id} in area {cust_area!r}"
    )


def test_clickstream_session_flow_get_location_never_returns_unknown_area(ctx):
    """
    Integration contract: every returned location must be a known
    area in the region_areas reference data.
    """
    customer = _build_customer_with_location(ctx)
    customer_id = customer["customer_id"]
    valid_areas = set(ctx.region_areas.areas)

    for _ in range(20):
        result = get_location(ctx, customer_id)
        assert result in valid_areas, f"get_location() returned unknown area {result!r}"


def test_clickstream_session_flow_get_location_missing_customer_returns_valid_area(
    ctx,
):
    """
    Integration contract: a non-existent customer_id must not raise
    and must still return a valid area (fallback path).
    """
    valid_areas = set(ctx.region_areas.areas)
    result = get_location(ctx, "NON_EXISTENT_CUST")
    assert result in valid_areas


# ============================================================
# decide_next_activity()
# ============================================================
# Integration contract: uses campaign + campaign assigment data


def test_clickstream_session_flow_decide_next_activity_returns_valid_decision(
    ctx, seed: int = 42
):
    """
    Integration contract: decide_next_activity() must always return
    one of three valid decisions regardless of customer/campaign state.
    """
    rng = random.Random(seed)
    customers_df = ctx.customers.customers_df
    digital = customers_df[
        customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
    ]
    if digital.empty:
        pytest.skip("No digital customers in generated data")

    customer = digital.sample(n=1, random_state=seed).iloc[0]
    customer_id = customer["customer_id"]
    customer_segment = customer["customer_segment"]
    signup_date = pd.Timestamp(customer["signup_date"])
    current_time = pd.Timestamp(signup_date) + pd.Timedelta(days=90)
    last_active_time = current_time - pd.Timedelta(days=5)

    decisions = set()
    for _ in range(30):
        d = decide_next_activity(
            ctx,
            activity_multiplier=rng.randint(1, 5),
            customer_id=customer_id,
            current_time=current_time,
            last_active_time=last_active_time,
            signup_date=signup_date,
            customer_segment=customer_segment,
            cart_content=[],
        )
        decisions.add(d)

    valid = {"Continue", "Inactive", "Churn"}
    assert decisions.issubset(valid), f"Unexpected decisions: {decisions - valid}"


def test_clickstream_session_flow_decide_next_activity_treatment_customer_continues_more_than_churn(
    ctx, seed: int = 42, N=1000
):
    """
    Integration contract: a customer in active Treatment campaign should
    have a higher Continue probability than Churn.
    """
    assign_df = ctx.campaign_assignments.campaign_assignments_df
    campaigns_df = ctx.campaigns.campaigns_df

    treatment_rows = assign_df[assign_df["assignment_group"] == "Treatment"]
    if treatment_rows.empty:
        pytest.skip("No treatment assignments in generated data")

    row = treatment_rows.sample(n=1, random_state=seed).iloc[0]
    customer_id = row["customer_id"]
    campaign = campaigns_df[campaigns_df["campaign_id"] == row["campaign_id"]].iloc[0]

    mid_campaign = (
        campaign["start_date"] + (campaign["end_date"] - campaign["start_date"]) / 2
    )
    customers_df = ctx.customers.customers_df
    cust_row = customers_df[customers_df["customer_id"] == customer_id].iloc[0]

    decisions = [
        decide_next_activity(
            ctx,
            activity_multiplier=3,
            customer_id=customer_id,
            current_time=mid_campaign,
            last_active_time=mid_campaign - pd.Timedelta(days=2),
            signup_date=pd.Timestamp(cust_row["signup_date"]),
            customer_segment=cust_row["customer_segment"],
            cart_content=[],
        )
        for _ in range(N)
    ]

    n_continue = decisions.count("Continue")
    n_churn = decisions.count("Churn")
    assert (
        n_continue > n_churn
    ), f"Expected Continue ({n_continue}) > Churn ({n_churn}) for treatment customer"


def test_clickstream_session_flow_decide_next_activity_test_high_spenders_continue_more_than_churn_risk(
    monkeypatch, ctx, seed: int = 42, N=1000
):
    """
    Integration contract: High Spenders should have a higher
    Continue probability than Churn Risk Customers
    """
    monkeypatch.setattr(
        "data_generation.services.clickstreams.clickstream_session_service.get_active_campaigns",
        lambda *args, **kwargs: None,
    )

    customers_df = ctx.customers.customers_df

    digital = customers_df[
        customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
    ]

    if digital.empty:
        pytest.skip("No digital customers in generated data")

    results = {}

    for segment in ["High Spenders", "Churn Risk Customers"]:
        candidates = digital[digital["customer_segment"] == segment]
        if candidates.empty:
            pytest.skip(f"No {segment} in generated data")

        segment_results = []
        sampled = candidates.sample(n=min(10, len(candidates)), random_state=seed)
        calls_each = max(1, N // len(sampled))

        for _, row in sampled.iterrows():
            signup_date = pd.Timestamp(row["signup_date"])
            current_time = signup_date + pd.Timedelta(days=90)
            last_active_time = current_time - pd.Timedelta(days=5)

            for _ in range(calls_each):
                segment_results.append(
                    decide_next_activity(
                        ctx,
                        activity_multiplier=3,
                        customer_id=row["customer_id"],
                        current_time=current_time,
                        last_active_time=last_active_time,
                        signup_date=signup_date,
                        customer_segment=row["customer_segment"],
                        cart_content=[],
                    )
                )

        results[segment] = segment_results

    high_spender_continue = results["High Spenders"].count("Continue")
    churn_risk_continue = results["Churn Risk Customers"].count("Continue")

    assert high_spender_continue > churn_risk_continue, (
        f"Expected High Spender Continue ({high_spender_continue}) > "
        f"Churn Risk Continue ({churn_risk_continue})"
    )


# ============================================================
# attempt_reactivation()
# ============================================================
# Integration contract: uses campaign assignment data


def test_clickstream_session_flow_attempt_reactivation_returns_none_or_future_timestamp(
    ctx, seed: int = 42, N=10
):
    """
    Integration contract: reactivation either returns None (stays
    inactive) or a timestamp strictly after current_time.
    """
    customers_df = ctx.customers.customers_df
    digital = customers_df[
        customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
    ]
    if digital.empty:
        pytest.skip("No digital customers")

    customer = digital.sample(n=1, random_state=seed).iloc[0]
    signup_date = customer["signup_date"]
    current_time = pd.Timestamp(signup_date) + pd.Timedelta(days=45)
    last_active = current_time - pd.Timedelta(days=30)

    for _ in range(N):
        result = attempt_reactivation(
            ctx,
            activity_multiplier=3,
            customer_id=customer["customer_id"],
            current_time=current_time,
            last_active_time=last_active,
            customer_segment=customer["customer_segment"],
            cart_content=[],
        )
        if result is not None:
            assert (
                pd.Timestamp(result) > current_time
            ), f"Reactivation time {result} must be after current_time {current_time}"


def test_clickstream_session_flow_attempt_reactivation_treatment_increases_reactivation_rate(
    ctx, seed: int = 42, N=1000
):
    """
    Integration contract: a customer in an active Treatment campaign
    must reactivate at a higher rate than a non-campaign customer.
    """
    assign_df = ctx.campaign_assignments.campaign_assignments_df
    campaigns_df = ctx.campaigns.campaigns_df
    customers_df = ctx.customers.customers_df

    treatment_rows = assign_df[assign_df["assignment_group"] == "Treatment"]
    if treatment_rows.empty:
        pytest.skip("No treatment assignments")

    row = treatment_rows.sample(n=1, random_state=seed).iloc[0]

    customer_id = row["customer_id"]
    cust = customers_df[customers_df["customer_id"] == customer_id].iloc[0]
    campaign = campaigns_df[campaigns_df["campaign_id"] == row["campaign_id"]].iloc[0]

    mid_campaign = (
        campaign["start_date"] + (campaign["end_date"] - campaign["start_date"]) / 2
    )
    last_active = mid_campaign - pd.Timedelta(days=25)

    reactivations_treatment = sum(
        1
        for _ in range(N)
        if attempt_reactivation(
            ctx,
            activity_multiplier=3,
            customer_id=customer_id,
            current_time=mid_campaign,
            last_active_time=last_active,
            customer_segment=cust["customer_segment"],
            cart_content=[],
        )
        is not None
    )

    # Non campaign customer: use a customer_id not in any campaign
    all_campaign_ids = set(assign_df["customer_id"])
    non_campaign_customers = customers_df[
        customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
        & ~customers_df["customer_id"].isin(all_campaign_ids)
    ]
    if non_campaign_customers.empty:
        pytest.skip("All digital customers have campaign assignments")

    nc_cust = non_campaign_customers.sample(n=1, random_state=seed).iloc[0]

    reactivations_no_campaign = sum(
        1
        for _ in range(N)
        if attempt_reactivation(
            ctx,
            activity_multiplier=3,
            customer_id=nc_cust["customer_id"],
            current_time=mid_campaign,
            last_active_time=last_active,
            customer_segment=nc_cust["customer_segment"],
            cart_content=[],
        )
        is not None
    )

    assert reactivations_treatment >= reactivations_no_campaign, (
        f"Treatment reactivations ({reactivations_treatment}) should be >= "
        f"no-campaign reactivations ({reactivations_no_campaign})"
    )


def test_clickstream_session_flow_attempt_reactivation_cart_content_decreases_reactivation_duration(
    ctx, seed: int = 42, N=1000
):
    """
    Integration contract: a customer with cart items must reactivate
    in a shorter duration than a customer with no cart items.
    """
    customers_df = ctx.customers.customers_df
    digital = customers_df[
        customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
    ]
    if digital.empty:
        pytest.skip("No digital customers")

    customer = digital.sample(n=1, random_state=seed).iloc[0]
    signup_date = customer["signup_date"]
    current_time = pd.Timestamp(signup_date) + pd.Timedelta(days=45)
    last_active = current_time - pd.Timedelta(days=30)

    cart_returns = []
    no_cart_returns = []

    for _ in range(N):
        r = attempt_reactivation(
            ctx,
            activity_multiplier=3,
            customer_id=customer["customer_id"],
            current_time=current_time,
            last_active_time=last_active,
            customer_segment=customer["customer_segment"],
            cart_content=["PROD001", "PROD002", "PROD003"],
        )
        if r is not None:
            cart_returns.append((r - current_time).days)

    for _ in range(N):
        r = attempt_reactivation(
            ctx,
            activity_multiplier=3,
            customer_id=customer["customer_id"],
            current_time=current_time,
            last_active_time=last_active,
            customer_segment=customer["customer_segment"],
            cart_content=[],
        )
        if r is not None:
            no_cart_returns.append((r - current_time).days)

    assert np.mean(cart_returns) <= np.mean(no_cart_returns)
