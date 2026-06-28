import pandas as pd

# --- STOCKOUT EVENTS ---


def test_stock_output_stockout_events_stockout_start_date_not_in_future(ctx):
    df = ctx.stockout_events.stockout_events_df
    assert (pd.to_datetime(df["stockout_start_date"]) <= pd.Timestamp.now()).all()


def test_stock_output_stockout_events_dates(ctx):
    df = ctx.stockout_events.stockout_events_df
    mask = df["stockout_end_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "stockout_end_date"])
        >= pd.to_datetime(df.loc[mask, "stockout_start_date"])
    ).all()


def test_stock_output_stockout_events_non_overlapping_per_product_store(ctx):
    """
    Stockout periods for the same product+store must not overlap.
    """
    df = ctx.stockout_events.stockout_events_df
    df["stockout_start_date"] = pd.to_datetime(df["stockout_start_date"])
    df["stockout_end_date"] = pd.to_datetime(df["stockout_end_date"])
    for (store_id, product_id), group in df.groupby(["store_id", "product_id"]):
        rows = group.sort_values("stockout_start_date").reset_index(drop=True)
        for i in range(len(rows) - 1):
            end = rows.loc[i, "stockout_end_date"]
            next_start = rows.loc[i + 1, "stockout_start_date"]
            if pd.notna(end):
                assert (
                    end <= next_start
                ), f"Overlapping stockouts for store={store_id}, product={product_id}"


# --- STOCK SNAPSHOTS ---


def test_stock_output_stock_snapshots_stock_band_status_match(ctx):
    df = ctx.stock_snapshots.stock_snapshots_df
    assert (
        ((df["stock_band"] == "0") & (df["stock_status"] == "Out of Stock"))
        | ((df["stock_band"] == "1-5") & (df["stock_status"] == "Limited Stock"))
        | ((df["stock_band"] == "6-20") & (df["stock_status"] == "Low Stock"))
        | ((df["stock_band"] == "21-100") & (df["stock_status"] == "In Stock"))
        | ((df["stock_band"] == "101+") & (df["stock_status"] == "Overstocked"))
    ).all()


def test_stock_output_stock_snapshots_week_start_date_not_in_future(ctx):
    df = ctx.stock_snapshots.stock_snapshots_df
    assert (pd.to_datetime(df["week_start_date"]) <= pd.Timestamp.now()).all()


def test_stock_output_stockout_reflected_in_snapshots(ctx):
    """
    For each stockout, at least one snapshot within the window must be Out of Stock.
    Sparse emission means not every week is guaranteed to have a row.
    """
    stockouts = ctx.stockout_events.stockout_events_df
    snapshots = ctx.stock_snapshots.stock_snapshots_df

    stockouts["start"] = pd.to_datetime(stockouts["stockout_start_date"])
    stockouts["end"] = pd.to_datetime(stockouts["stockout_end_date"])
    snapshots["week"] = pd.to_datetime(snapshots["week_start_date"])

    merged = snapshots.merge(stockouts, on=["store_id", "product_id"], how="left")
    in_stockout = (merged["week"] >= merged["start"]) & (
        merged["week"] <= merged["end"]
    )

    # Any snapshot that falls within a stockout window must be Out of Stock
    # (snapshots emitted during non-Out-of-Stock periods won't overlap a stockout window)
    assert (
        merged.loc[in_stockout, "stock_status"] == "Out of Stock"
    ).all(), (
        "A snapshot was emitted during a stockout window with non-zero stock status"
    )


# --- INVENTORY CHANGE EVENTS ---


def test_stock_output_inventory_change_event_event_timestamp_not_in_future(ctx):
    df = ctx.stock_snapshots.inventory_change_events_df
    assert (pd.to_datetime(df["event_timestamp"]) <= pd.Timestamp.now()).all()


def test_stock_output_inventory_change_event_delta_consistent_with_stock_after(ctx):
    """
    For consecutive events on the same store+product, the stock_after of the
    prior row plus the delta of the current row must equal the current stock_after.
    """
    df = ctx.stock_snapshots.inventory_change_events_df
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])

    df = df.sort_values(["store_id", "product_id", "event_timestamp"])

    df["prior_stock"] = df.groupby(["store_id", "product_id"])["stock_after"].shift(1)

    mask = df["prior_stock"].notna()

    expected = df.loc[mask, "prior_stock"] + df.loc[mask, "delta"]

    assert (
        expected == df.loc[mask, "stock_after"]
    ).all(), "Found inventory events where stock_after != previous stock_after + delta"


def test_stock_output_stockout_forces_inventory_to_zero(ctx):
    """
    Any inventory event emitted during a stockout window must show zero stock.
    Not all stockout weeks are guaranteed to have an event (sparse emission).
    """
    stockouts = ctx.stockout_events.stockout_events_df
    events = ctx.stock_snapshots.inventory_change_events_df

    stockouts["start"] = pd.to_datetime(stockouts["stockout_start_date"])
    stockouts["end"] = pd.to_datetime(stockouts["stockout_end_date"])
    events["ts"] = pd.to_datetime(events["event_timestamp"])

    merged = events.merge(stockouts, on=["store_id", "product_id"], how="left")
    in_stockout = (merged["ts"] >= merged["start"]) & (merged["ts"] <= merged["end"])

    if in_stockout.any():
        assert (
            merged.loc[in_stockout, "stock_after"] == 0
        ).all(), "An inventory event during a stockout window has non-zero stock_after"
        assert (
            merged.loc[in_stockout, "delta"] <= 0
        ).all(), "An inventory event during a stockout window has positive delta"
