import pandas as pd

# --- STOCKOUT EVENTS ---


def test_stockout_events_stockout_start_date_not_in_future(dataframes):
    df = dataframes["stockout_events"].copy()
    assert (pd.to_datetime(df["stockout_start_date"]) <= pd.Timestamp.now()).all()


def test_stockout_events_dates(dataframes):
    df = dataframes["stockout_events"].copy()
    mask = df["stockout_end_date"].notna()
    assert (
        pd.to_datetime(df.loc[mask, "stockout_end_date"])
        >= pd.to_datetime(df.loc[mask, "stockout_start_date"])
    ).all()


def test_stockout_events_non_overlapping_per_product_store(dataframes):
    """
    Stockout periods for the same product+store must not overlap.
    """
    df = dataframes["stockout_events"].copy()
    df["stockout_start_date"] = pd.to_datetime(df["stockout_start_date"])
    df["stockout_end_date"] = pd.to_datetime(df["stockout_end_date"])
    for (store_id, product_id), group in df.groupby(["store_id", "product_id"]):
        rows = group.sort_values("stockout_start_date").reset_index(drop=True)
        for i in range(len(rows) - 1):
            end = rows.loc[i, "stockout_end_date"]
            next_start = rows.loc[i + 1, "stockout_start_date"]
            if pd.notna(end):
                assert (
                    end < next_start
                ), f"Overlapping stockouts for store={store_id}, product={product_id}"


# --- STOCK SNAPSHOTS ---


def test_stock_snapshots_stock_band_status_match(dataframes):
    df = dataframes["stock_snapshots"].copy()
    assert (
        ((df["stock_band"] == "0") & (df["stock_status"] == "Out of Stock"))
        | ((df["stock_band"] == "1-5") & (df["stock_status"] == "Limited Stock"))
        | ((df["stock_band"] == "6-20") & (df["stock_status"] == "Low Stock"))
        | ((df["stock_band"] == "21-100") & (df["stock_status"] == "In Stock"))
        | ((df["stock_band"] == "101+") & (df["stock_status"] == "Overstocked"))
    ).all()


def test_stock_snapshots_week_start_date_not_in_future(dataframes):
    df = dataframes["stock_snapshots"].copy()
    assert (pd.to_datetime(df["week_start_date"]) <= pd.Timestamp.now()).all()


# --- INVENTORY CHANGE EVENTS ---


def test_inventory_change_event_event_timestamp_not_in_future(dataframes):
    df = dataframes["inventory_change_events"].copy()
    assert (pd.to_datetime(df["event_timestamp"]) <= pd.Timestamp.now()).all()


def test_inventory_change_event_delta_consistent_with_stock_after(dataframes):
    """
    For consecutive events on the same store+product, the stock_after of the
    prior row plus the delta of the current row must equal the current stock_after.
    """
    df = dataframes["inventory_change_events"].copy()
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])

    df = df.sort_values(["store_id", "product_id", "event_timestamp"])

    df["prior_stock"] = df.groupby(["store_id", "product_id"])["stock_after"].shift(1)

    mask = df["prior_stock"].notna()

    expected = df.loc[mask, "prior_stock"] + df.loc[mask, "delta"]

    assert (
        expected == df.loc[mask, "stock_after"]
    ).all(), "Found inventory events where stock_after != previous stock_after + delta"
