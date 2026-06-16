from collections import Counter

import pandas as pd


def test_clickstream_has_treatment_campaign(dataframes):
    df = dataframes["clickstreams"].copy()
    assert (
        ~df["has_treatment_campaign"]
        | df["campaign_ids"].apply(lambda x: x is not None and len(x) > 0)
    ).all()


def test_clickstream_bounce_flag(dataframes):
    df = dataframes["clickstreams"].copy()

    # Bounce rows can only be the first event
    assert ((df["bounce_flag"] == 0) | (df["event_order"] == 1)).all()

    for _, session in df.groupby("session_id"):
        if session["bounce_flag"].iloc[0] == 1:
            # Session contains exactly one event
            assert len(session) == 1


def test_session_has_entry_point(dataframes):
    df = dataframes["clickstreams"].copy()
    valid_entry_points = ["Home View", "Search View", "Category View", "Product View"]
    for session_id, session in df.groupby("session_id"):
        assert any(
            e in session["event_type"].values for e in valid_entry_points
        ), f"Session {session_id} has no entry point event"


def test_clickstream_session_order_contract(dataframes):
    df = dataframes["clickstreams"].copy()
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])

    for _, session in df.groupby("session_id"):
        sorted_session = session.sort_values("event_timestamp")

        # event_timestamp monotonic
        assert sorted_session["event_timestamp"].is_monotonic_increasing

        # event_order must match sorted position
        assert sorted_session["event_order"].tolist() == list(
            range(1, len(session) + 1)
        )

        # event_order must match event_timestamp order (bidirectional guarantee)
        assert (
            session.sort_values("event_order")["event_timestamp"].tolist()
            == sorted_session["event_timestamp"].tolist()
        )


def test_clickstream_event_timestamp_not_in_future(dataframes):
    df = dataframes["clickstreams"].copy()
    assert (pd.to_datetime(df["event_timestamp"]) <= pd.Timestamp.now()).all()


def test_clickstream_product_name_valid(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        pid = r["product_id"]
        if pid and isinstance(pid, str) and pid.strip():
            assert (
                isinstance(r["product_name"], str) and len(r["product_name"]) > 0
            ), f"Missing product_name for product_id={pid}"


def test_clickstream_product_category_consistency(dataframes):
    df = dataframes["clickstreams"].copy()
    products = dataframes["products"]

    product_category_map = dict(zip(products["product_id"], products["category"]))

    for r in df.to_dict("records"):
        pid = r["product_id"]
        if pd.notna(pid) and pid != "":
            assert r["category"] == product_category_map[pid]


def test_clickstream_cart_contains_added_products(dataframes):
    df = dataframes["clickstreams"].copy()
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])

    for session_id, session in df.groupby("session_id"):
        session = session.sort_values("event_order")
        rows = session.to_dict("records")

        for i in range(1, len(rows)):
            prev_cart = Counter(rows[i - 1].get("cart_content") or [])
            curr_cart = Counter(rows[i].get("cart_content") or [])

            event_type = rows[i]["event_type"]
            pid = rows[i].get("product_id")

            if event_type == "Add to Cart" and pid is not None:

                # Added product must have increased by exactly 1
                assert curr_cart[pid] == prev_cart[pid] + 1, (
                    f"Product {pid} not correctly added in session {session_id} "
                    f"(before={prev_cart[pid]}, after={curr_cart[pid]})"
                )

                # All other products must remain unchanged
                for p in set(prev_cart.keys()) | set(curr_cart.keys()):
                    if p != pid:
                        assert (
                            curr_cart[p] == prev_cart[p]
                        ), f"Cart changed incorrectly for product {p} in session {session_id}"


def test_clickstream_cart_does_not_contain_removed_products(dataframes):
    df = dataframes["clickstreams"].copy()
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])

    for session_id, session in df.groupby("session_id"):
        session = session.sort_values("event_order")
        rows = session.to_dict("records")

        for i in range(1, len(rows)):
            prev_cart = Counter(rows[i - 1].get("cart_content") or [])
            curr_cart = Counter(rows[i].get("cart_content") or [])

            event_type = rows[i]["event_type"]
            pid = rows[i].get("product_id")

            if event_type == "Remove from Cart" and pid is not None:

                # Removed product must have decreased by exactly 1
                assert curr_cart[pid] == prev_cart[pid] - 1, (
                    f"Product {pid} not correctly removed in session {session_id} "
                    f"(before={prev_cart[pid]}, after={curr_cart[pid]})"
                )

                # All other products must remain unchanged
                for p in set(prev_cart.keys()) | set(curr_cart.keys()):
                    if p != pid:
                        assert (
                            curr_cart[p] == prev_cart[p]
                        ), f"Cart changed incorrectly for product {p} in session {session_id}"


def test_clickstream_cart_size_matches_cart_content(dataframes):
    df = dataframes["clickstreams"].copy()
    for _, row in df.iterrows():
        cart_content = row["cart_content"] or []
        assert len(cart_content) == row["cart_size"]


def test_clickstream_cart_size_changes(dataframes):
    df = dataframes["clickstreams"].copy()
    for _, session in df.groupby("session_id"):
        session = session.sort_values("event_order")
        cart_size = session["cart_size"].tolist()
        event_types = session["event_type"].tolist()

        for prev, curr, event in zip(cart_size, cart_size[1:], event_types[1:]):
            if event in ["Remove from Cart", "Payment Successful"]:
                assert curr < prev
            elif event == "Add to Cart":
                assert curr > prev
            else:
                assert curr == prev


def test_clickstream_purchased_items_event_type(dataframes):
    df = dataframes["clickstreams"].copy()
    assert (
        df["purchased_items"].apply(lambda x: x is not None and len(x) > 0)
        | (df["event_type"] != "Payment Successful")
    ).all()


def test_clickstream_purchased_items_subset_of_cart(dataframes):
    df = dataframes["clickstreams"].copy()
    for _, session in df.groupby("session_id"):
        session = session.sort_values("event_order").reset_index(drop=True)
        for i, row in session.iterrows():
            if row["event_type"] == "Payment Successful":
                purchased_items = set(row["purchased_items"] or [])
                if i == 0:
                    # No prior row — purchased items must be empty (edge case)
                    assert len(purchased_items) == 0
                else:
                    prior_cart = set(session.loc[i - 1, "cart_content"] or [])
                    assert purchased_items.issubset(prior_cart), (
                        f"purchased_items {purchased_items} not subset of prior cart "
                        f"{prior_cart} in session {row['session_id']}"
                    )


def test_clickstream_event_remove_from_cart(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Remove from Cart":
            assert pd.notna(r["product_id"]) or r["product_id"] != ""
            assert pd.notna(r["category"]) or r["category"] != ""
            assert r["page"] is not None and "remove_from_cart" in r["page"]


def test_clickstream_event_add_to_cart(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Add to Cart":
            assert pd.notna(r["product_id"]) or r["product_id"] != ""
            assert pd.notna(r["category"]) or r["category"] != ""
            assert pd.notna(r["page"]) and "add_to_cart" in r["page"]
            assert (r["cart_content"] is not None) and (len(r["cart_content"]) > 0)
            assert r["cart_size"] > 0


def test_clickstream_event_product_view(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Product View":
            assert pd.notna(r["product_id"]) or r["product_id"] != ""
            assert pd.notna(r["category"]) or r["category"] != ""
            assert pd.notna(r["page"]) and "product" in r["page"]


def test_clickstream_event_category_view(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Category View":
            assert pd.notna(r["category"]) or r["category"] != ""
            assert pd.notna(r["page"]) and "category" in r["page"]


def test_clickstream_event_search_view(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Search View":
            assert pd.notna(r["product_id"]) or r["product_id"] != ""
            assert pd.notna(r["category"]) or r["category"] != ""
            assert pd.notna(r["page"]) and "search" in r["page"]


def test_clickstream_event_payment_successful(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Payment Successful":
            assert r["purchased_items"] is not None and len(r["purchased_items"]) > 0
            assert pd.notna(r["page"]) and "payment/success" in r["page"]


def test_clickstream_event_home_view(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Home View":
            assert pd.notna(r["product_id"]) or r["product_id"] != ""
            assert pd.notna(r["category"]) or r["category"] != ""
            assert pd.notna(r["page"]) and "home" in r["page"]


def test_clickstream_event_cart_view(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] == "Cart View":
            assert pd.notna(r["product_id"]) or r["product_id"] != ""
            assert pd.notna(r["category"]) or r["category"] != ""
            assert pd.notna(r["page"]) and "cart" in r["page"]


def test_clickstream_event_checkout(dataframes):
    df = dataframes["clickstreams"].copy()
    for r in df.to_dict("records"):
        if r["event_type"] in ["Checkout Start", "Payment Attempt", "Payment Failed"]:
            assert (r["cart_content"] is not None) and (len(r["cart_content"]) > 0)
            assert r["cart_size"] > 0
            assert (
                isinstance(r["purchased_items"], list)
                and len(r["purchased_items"]) == 0
            )
            assert pd.notna(r["page"]) and any(
                x in r["page"] for x in ["checkout", "payment"]
            )


def test_clickstream_payment_sequence(dataframes):
    """
    Within a session, Payment Successful / Payment Failed must be preceded
    by at least one Payment Attempt, which must be preceded by a Checkout Start.
    """
    df = dataframes["clickstreams"].copy()
    payment_terminal = {"Payment Successful", "Payment Failed"}
    for _, session in df.groupby("session_id"):
        session = session.sort_values("event_order")
        event_types = session["event_type"].tolist()
        if any(e in payment_terminal for e in event_types):
            assert (
                "Payment Attempt" in event_types
            ), "Payment terminal event without Payment Attempt in session"
            assert (
                "Checkout Start" in event_types
            ), "Payment terminal event without Checkout Start in session"
