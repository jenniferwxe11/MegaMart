import pandas as pd

# --- BUNDLE PRICINGS ---


def test_bundle_output_pricings_dates(ctx):
    df = ctx.bundles.bundle_pricings_df
    assert (
        pd.to_datetime(df["effective_start_date"])
        <= pd.to_datetime(df["effective_end_date"])
    ).all()


def test_bundle_output_pricings_discount_value_less_than_bundle_price(ctx):
    df = ctx.bundles.bundle_pricings_df
    assert (df["discount_value"] <= df["bundle_price"]).all()


def test_bundle_output_pricings_non_overlapping_dates_per_bundle(ctx):
    """
    No two pricing rows for the same bundle should have overlapping date ranges.
    """
    df = ctx.bundles.bundle_pricings_df
    df["effective_start_date"] = pd.to_datetime(df["effective_start_date"])
    df["effective_end_date"] = pd.to_datetime(df["effective_end_date"])
    for bundle_id, group in df.groupby("bundle_id"):
        rows = group.sort_values("effective_start_date").reset_index(drop=True)
        for i in range(len(rows) - 1):
            assert (
                rows.loc[i, "effective_end_date"]
                < rows.loc[i + 1, "effective_start_date"]
            ), f"Overlapping pricing periods for bundle {bundle_id}"


def test_bundle_output_pricings_cover_full_window(ctx):
    df = ctx.bundles.bundle_pricings_df
    df["effective_start_date"] = pd.to_datetime(df["effective_start_date"])
    df["effective_end_date"] = pd.to_datetime(df["effective_end_date"])

    for bundle_id, phases in df.groupby("bundle_id"):
        phases = phases.sort_values("effective_start_date").reset_index(drop=True)

        for i in range(len(phases) - 1):
            assert (
                phases.loc[i, "effective_end_date"] + pd.Timedelta(days=1)
                == phases.loc[i + 1, "effective_start_date"]
            ), f"Gap in pricing phases for bundle {bundle_id}"


def test_bundle_output_pricings_launch_always_first(ctx):
    df = ctx.bundles.bundle_pricings_df
    df["effective_start_date"] = pd.to_datetime(df["effective_start_date"])

    for bundle_id, phases in df.groupby("bundle_id"):
        phases = phases.sort_values("effective_start_date")
        assert (
            phases.iloc[0]["pricing_phase"] == "LAUNCH"
        ), f"First phase is not LAUNCH for bundle {bundle_id}"


def test_bundle_output_pricing_phases_ordered(ctx):
    df = ctx.bundles.bundle_pricings_df
    df["effective_start_date"] = pd.to_datetime(df["effective_start_date"])

    for _, phases in df.groupby("bundle_id"):
        phases = phases.sort_values("effective_start_date")
        assert phases["effective_start_date"].is_monotonic_increasing
