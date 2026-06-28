import ast

import pandas as pd

# --- CAMPAIGNS ---


def test_campaign_output_dates(ctx):
    df = ctx.campaigns.campaigns_df
    assert (pd.to_datetime(df["start_date"]) <= pd.to_datetime(df["end_date"])).all()


def test_campaign_output_status_aligned_with_dates(ctx):
    df = ctx.campaigns.campaigns_df
    assert (
        (df["status"] != "Completed")
        | (pd.to_datetime(df["end_date"]) <= pd.Timestamp.now())
    ).all()


# --- CAMPAIGN ASSIGNMENTS ---


def test_campaign_output_ab_test_when_valid_has_control_and_treatment(ctx):
    """
    A/B test campaigns must have both Treatment and Control assignment groups.
    """
    campaigns = ctx.campaigns.campaigns_df
    assignments = ctx.campaign_assignments.campaign_assignments_df
    ab_campaigns = campaigns[campaigns["is_ab_test"]]["campaign_id"]
    for camp_id in ab_campaigns:
        campaign_assign = assignments[assignments["campaign_id"] == camp_id]

        # Skip invalid experiments
        if campaign_assign.empty:
            continue

        groups = set(campaign_assign["assignment_group"].unique())
        assert (
            "Treatment" in groups and "Control" in groups
        ), f"A/B campaign {camp_id} missing Treatment or Control group"


# --- CAMPAIGN EXPOSURE ---


def test_campaign_output_channels_match_exposures(ctx):
    """
    Every channel in campaign_exposures must be a channel listed for that campaign.
    """
    campaigns = ctx.campaigns.campaigns_df
    exposures = ctx.campaign_assignments.campaign_exposures_df
    camp_channel_map = {}
    for _, row in campaigns.iterrows():
        channels = row["channels"]
        if isinstance(channels, list):
            camp_channel_map[row["campaign_id"]] = set(channels)
        elif isinstance(channels, str):
            try:
                camp_channel_map[row["campaign_id"]] = set(ast.literal_eval(channels))
            except Exception:
                camp_channel_map[row["campaign_id"]] = {channels}

    for _, row in exposures.iterrows():
        camp_id = row["campaign_id"]
        if camp_id in camp_channel_map:
            assert (
                row["channel"] in camp_channel_map[camp_id]
            ), f"Channel '{row['channel']}' not in campaign {camp_id} channels"


def test_campaign_output_exposure_assignment_group_consistent(ctx):
    """
    A customer's assignment group for a given campaign must be consistent
    across all channels (same customer can't be Treatment in Email and Control in Push).
    """
    df = ctx.campaign_assignments.campaign_exposures_df
    grouped = df.groupby(["campaign_id", "customer_id"])["assignment_group"].nunique()
    assert (
        grouped == 1
    ).all(), "Customer has inconsistent assignment groups within a campaign's exposure channels."


def test_campaign_output_exposure_control_group_not_exposed(ctx):
    """
    Control group members should not be exposed.
    """
    df = ctx.campaign_assignments.campaign_exposures_df
    control = df[df["assignment_group"] == "Control"]
    assert (~control["exposed"]).all(), "Control group members should not be exposed"


def test_campaign_output_exposure_exposed_time_not_in_future(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    mask = df["exposed_time"].notna()
    assert (pd.to_datetime(df.loc[mask, "exposed_time"]) <= pd.Timestamp.now()).all()


def test_campaign_output_exposure_exposed_have_exposed_time(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    assert (df["exposed_time"].notna() | ~df["exposed"]).all()


def test_campaign_output_exposure_exposed_time_within_campaign_dates(ctx):
    """
    Exposure timestamps must fall within the campaign's active window.
    """
    campaigns = ctx.campaigns.campaigns_df
    exposures = ctx.campaign_assignments.campaign_exposures_df
    merged = exposures.merge(
        campaigns[["campaign_id", "start_date", "end_date"]],
        on="campaign_id",
        how="left",
    )
    mask = merged["exposed_time"].notna()
    sub = merged[mask].copy()
    assert (
        pd.to_datetime(sub["exposed_time"]) >= pd.to_datetime(sub["start_date"])
    ).all(), "Exposure time before campaign start date"
    assert (
        pd.to_datetime(sub["exposed_time"]) <= pd.to_datetime(sub["end_date"])
    ).all(), "Exposure time after campaign end date"


def test_campaign_output_exposure_opened(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    assert (~df["opened"] | df["exposed"]).all()


def test_campaign_output_exposure_opened_time_not_in_future(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    mask_notna = df["opened_time"].notna()
    assert (
        pd.to_datetime(df.loc[mask_notna, "opened_time"]) <= pd.Timestamp.now()
    ).all()


def test_campaign_output_exposure_opened_have_opened_time(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    assert (df["opened_time"].notna() | ~df["opened"]).all()


def test_campaign_output_exposure_opened_time_after_exposed_time(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    mask_both = df["opened_time"].notna() & df["exposed_time"].notna()
    assert (
        pd.to_datetime(df.loc[mask_both, "opened_time"])
        >= pd.to_datetime(df.loc[mask_both, "exposed_time"])
    ).all()


def test_campaign_output_exposure_opened_time_within_campaign_dates(ctx):
    """
    Opened timestamps must fall within the campaign's active window.
    """
    campaigns = ctx.campaigns.campaigns_df
    exposures = ctx.campaign_assignments.campaign_exposures_df
    merged = exposures.merge(
        campaigns[["campaign_id", "start_date", "end_date"]],
        on="campaign_id",
        how="left",
    )
    mask = merged["opened_time"].notna()
    sub = merged[mask].copy()
    assert (
        pd.to_datetime(sub["opened_time"]) >= pd.to_datetime(sub["start_date"])
    ).all(), "Opened time before campaign start date"
    assert (
        pd.to_datetime(sub["opened_time"]) <= pd.to_datetime(sub["end_date"])
    ).all(), "Opened time after campaign end date"


def test_campaign_output_exposure_clicked(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    assert (
        ~df["clicked"]
        | df["opened"]
        | df["channel"].isin(["Paid Advertisements", "In-App"])
    ).all()


def test_campaign_output_exposure_clicked_time_not_in_future(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    mask_notna = df["clicked_time"].notna()
    assert (
        pd.to_datetime(df.loc[mask_notna, "clicked_time"]) <= pd.Timestamp.now()
    ).all()


def test_campaign_output_exposure_clicked_have_clicked_time(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    assert (df["clicked_time"].notna() | ~df["clicked"]).all()


def test_campaign_output_exposure_clicked_time_after_opened_time(ctx):
    df = ctx.campaign_assignments.campaign_exposures_df
    mask_both = df["clicked_time"].notna() & df["opened_time"].notna()
    assert (
        pd.to_datetime(df.loc[mask_both, "clicked_time"])
        >= pd.to_datetime(df.loc[mask_both, "opened_time"])
    ).all()


def test_campaign_output_exposure_clicked_time_within_campaign_dates(ctx):
    """
    Clicked timestamps must fall within the campaign's active window.
    """
    campaigns = ctx.campaigns.campaigns_df
    exposures = ctx.campaign_assignments.campaign_exposures_df
    merged = exposures.merge(
        campaigns[["campaign_id", "start_date", "end_date"]],
        on="campaign_id",
        how="left",
    )
    mask = merged["clicked_time"].notna()
    sub = merged[mask].copy()
    assert (
        pd.to_datetime(sub["clicked_time"]) >= pd.to_datetime(sub["start_date"])
    ).all(), "Clicked time before campaign start date"
    assert (
        pd.to_datetime(sub["clicked_time"]) <= pd.to_datetime(sub["end_date"])
    ).all(), "Clicked time after campaign end date"
