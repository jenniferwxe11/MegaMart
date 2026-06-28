import copy
import random
import uuid
from datetime import timedelta
from typing import Any

import pandas as pd

from data_generation.config.campaigns_config import CAMPAIGN_PEAK_CATEGORIES
from data_generation.config.clickstreams_config import (
    FIRST_SESSION_WINDOW_DAYS,
    IN_STOCK_STATUS,
    LANDING_PAGE_BEHAVIOUR,
    MAX_ACTIVITY_MULTIPLIER,
    MAX_LOOK_AHEAD_DAYS,
    MISSION_EFFICIENCY,
    MISSION_MAX_MULTIPLIER,
    REFERRER_DISTRIBUTION,
    SEASONAL_UPLIFT,
    SEGMENT_MISSION_BIAS,
    SESSION_MISSION_TARGET_RANGE,
    VALID_EVENT_TRANSITIONS,
)
from data_generation.config.constants import DATA_END_DATE
from data_generation.config.generation_config import (
    LIMIT_CLICKSTREAM_EVENTS,
    NUM_CLICKSTREAM_SESSIONS,
)
from data_generation.config.products_config import CATEGORY_AFFINITY
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.clickstreams.clickstream_event_service import (
    resolve_add_to_cart,
    resolve_category_view,
    resolve_page,
    resolve_payment_successful,
    resolve_product_view,
    resolve_remove_from_cart,
    resolve_scroll_and_time,
    resolve_search_view,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    check_promotion_eligibility,
    get_active_campaigns,
    get_location,
    get_product_stock_status,
    get_relevant_promotion_on_page,
)
from data_generation.services.clickstreams.clickstream_promotion_service import (
    process_promotion_exposure,
)
from data_generation.services.clickstreams.clickstream_session_service import (
    attempt_reactivation,
    decide_next_activity,
    generate_activity_multiplier,
    generate_timestamp,
    sample_inactive_gap,
    sample_session_gap,
)
from data_generation.services.clickstreams.clickstream_transition_service import (
    TransitionMatrix,
    apply_mission_bias,
    apply_promotion_uplift,
    apply_purchase_progress_bias,
    apply_seasonal_uplift,
    apply_stock_status_uplift,
    get_base_transition_probability,
    normalise_probability,
)
from data_generation.utils.date_time_utils import (
    get_day_type,
    get_pay_cycle,
    get_seasonal_event,
    get_time_of_day,
)
from data_generation.utils.io_utils import save


@register("clickstreams_generator")
def clickstreams_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    product_ids = ctx.products.product_ids
    product_name_map = ctx.products.product_name_map
    product_category_map = ctx.products.product_category_map
    online_store_id = ctx.stores.online_store_id
    customers_df = ctx.customers.customers_df

    # Assumption: Clickstream tracking is only available for users with digital activity
    customers_df = customers_df[
        customers_df["customer_type"].isin(["Online Only", "Omnichannel"])
    ].copy()

    # ---------------------------
    # Storage
    # ---------------------------

    clickstreams: list[dict[str, Any]] = []

    # ---------------------------
    # Generation: Customer Loop
    # ---------------------------

    total_sessions = 0
    total_events = 0
    for _, customer in customers_df.iterrows():

        if (
            total_sessions >= NUM_CLICKSTREAM_SESSIONS
            or total_events >= LIMIT_CLICKSTREAM_EVENTS
        ):
            break

        # --- Customer Context ---
        customer_id = customer["customer_id"]
        customer_segment = customer["customer_segment"]
        signup_date = customer["signup_date"]

        # --- First Session Initialisation ---
        current_time = generate_timestamp(
            pd.Timestamp(signup_date),
            min(
                pd.Timestamp(signup_date) + timedelta(days=FIRST_SESSION_WINDOW_DAYS),
                pd.Timestamp(DATA_END_DATE),
            ),
        ).replace(microsecond=0)

        last_active_time = current_time
        customer_cart: list[str] = []
        # Higher = more frequent sessions
        activity_multiplier = min(
            generate_activity_multiplier(), MAX_ACTIVITY_MULTIPLIER
        )

        # ---------------------------
        # Generation: Session Loop
        # ---------------------------

        session_index = 0
        while pd.Timestamp(current_time) <= pd.Timestamp(DATA_END_DATE):

            if (
                total_sessions >= NUM_CLICKSTREAM_SESSIONS
                and total_events >= LIMIT_CLICKSTREAM_EVENTS
            ):
                break

            # --- Session Context ---
            session_id = str(uuid.uuid4())
            session_start_time = current_time
            time_of_day = get_time_of_day(session_start_time)
            day_type = get_day_type(session_start_time)
            pay_cycle = get_pay_cycle(session_start_time)
            season, season_type = get_seasonal_event(session_start_time)

            # --- Campaign Context ---
            active_campaigns = get_active_campaigns(
                ctx, customer_id, session_start_time
            )
            campaign_ids = (
                []
                if active_campaigns is None
                else active_campaigns["campaign_id"].unique().tolist()
            )
            has_treatment = (
                active_campaigns is not None
                and (active_campaigns["assignment_group"] == "Treatment").any()
            )
            has_control = (
                active_campaigns is not None
                and (active_campaigns["assignment_group"] == "Control").any()
            )
            eligible_promotions = check_promotion_eligibility(
                ctx, session_start_time, active_campaigns
            )

            # --- Traffic Source ---
            referrer = random.choices(
                list(REFERRER_DISTRIBUTION.keys()),
                weights=list(REFERRER_DISTRIBUTION.values()),
            )[0]
            location = get_location(
                ctx,
                customer_id,
            )
            device_category = customer["device_category"]

            # --- Session Mission ---
            mission_weights = SEGMENT_MISSION_BIAS.get(customer_segment, {})
            missions = list(SESSION_MISSION_TARGET_RANGE.keys())
            mission_choice = random.choices(
                missions, weights=[mission_weights.get(m, 0.0) for m in missions]
            )[0]
            eff_min, eff_max = MISSION_EFFICIENCY.get(mission_choice, (0.0, 1.0))
            mission_efficiency = random.uniform(eff_min, eff_max)

            # --- Event Count Estimation ---
            min_target, max_target = SESSION_MISSION_TARGET_RANGE.get(
                mission_choice, (3, 10)
            )
            target_cart_size = random.randint(min_target, max_target)
            base_event_count: int = int(target_cart_size / mission_efficiency)

            # --- Session Multipliers ---
            extra_events: int = 0
            for s in [time_of_day, day_type, pay_cycle, season]:
                if s and s in SEASONAL_UPLIFT:
                    min_event, max_event = SEASONAL_UPLIFT[s].get(
                        "extra_events", (0, 0)
                    )
                    extra_events += random.randint(min_event, max_event)

            extra_multiplier = 1.0
            if has_treatment:
                extra_multiplier *= 1.1
            if eligible_promotions:
                extra_multiplier *= 1.2
            if customer_segment == "High Spenders":
                extra_multiplier *= 1.1
            if customer_segment == "Churn Risk Customers":
                extra_multiplier *= 0.9
            # Clamp to prevent explosion
            extra_multiplier = min(
                extra_multiplier, MISSION_MAX_MULTIPLIER.get(mission_choice, 1.5)
            )

            # --- Final Event Count ---
            _scaled: float = (
                (base_event_count + extra_events)
                * extra_multiplier
                * random.uniform(0.85, 1.15)
            )
            _raw_count: int = int(_scaled)
            event_count: int = _raw_count if _raw_count > 1 else 1
            bounce_flag = 1 if event_count == 1 else 0

            # Session State
            event_order = 1
            events: list[str] = []

            # --- Build Session Affinity Cluster ---
            num_seeds = random.randint(1, 3)
            seed_categories = [
                product_category_map.get(random.choice(product_ids))
                for _ in range(num_seeds)
            ]
            session_affinity_categories = set()
            for seed in seed_categories:
                if seed:
                    session_affinity_categories.add(seed)
                    session_affinity_categories.update(CATEGORY_AFFINITY.get(seed, []))

            # Create session-level cart snapshot
            session_cart_snapshot = customer_cart.copy()

            # Session level promotion memory
            selected_promotions: list[dict] = []
            seen_promotions: dict[str, int] = {}
            seen_promo_types: dict[str, int] = {}

            # Store details of previous event to apply sequential biases and effects
            previous_event: dict[str, Any] = {
                "event_type": None,
                "category": None,
                "product_id": None,
                "search_term": None,
                "timestamp": None,
                "time_on_page": None,
                "cart_content": session_cart_snapshot,
                "pending_events": [],
            }

            # Transition Probabilities
            transition_probability: dict[str, dict[str, float]] = copy.deepcopy(
                VALID_EVENT_TRANSITIONS
            )

            # Applies for all the events in the session
            transition_probability = normalise_probability(
                get_base_transition_probability(
                    transition_probability,
                    customer_segment,
                    has_treatment,
                )
            )

            # ---------------------------
            # Generation: Event Loop
            # ---------------------------

            for event_index in range(event_count):
                clickstream_id = f"{session_id}_{event_index}"

                # Get previous event details
                previous_event_type: str = str(previous_event.get("event_type") or "")
                previous_product_id: str = str(previous_event.get("product_id") or "")
                previous_category: str = str(previous_event.get("category") or "")
                previous_search_term: str = str(previous_event.get("search_term") or "")
                previous_timestamp = previous_event.get("timestamp", None)
                previous_time_on_page = previous_event.get("time_on_page", None)

                # Initialise current event details
                event_type = category = product_id = product_name = search_term = (
                    timestamp
                ) = None
                cart_content = (previous_event.get("cart_content") or []).copy()
                pending_events = (previous_event.get("pending_events") or []).copy()
                purchased_items = []
                time_on_page = scroll_depth = stock_status = promotion_ids = (
                    bundle_ids
                ) = None

                event_tp: TransitionMatrix = copy.deepcopy(transition_probability)

                # --- First Event (Landing) ---
                if event_order == 1:
                    landing_behaviour = LANDING_PAGE_BEHAVIOUR.get(
                        referrer, LANDING_PAGE_BEHAVIOUR["direct"]
                    )
                    event_type = random.choices(
                        list(landing_behaviour.keys()),
                        weights=list(landing_behaviour.values()),
                    )[0]
                    # Introduce delay after session start time
                    timestamp = (
                        session_start_time + timedelta(seconds=random.randint(1, 300))
                    ).replace(microsecond=0)

                # --- Second to Last Event ---
                else:
                    # Event timestamp based on previous event time on page with idle time
                    assert (
                        previous_timestamp is not None
                        and previous_time_on_page is not None
                    )
                    prev_top = (
                        previous_time_on_page
                        if isinstance(previous_time_on_page, timedelta)
                        else timedelta(seconds=0)
                    )

                    timestamp = (
                        previous_timestamp
                        + prev_top
                        + timedelta(seconds=random.randint(5, 180))
                    ).replace(microsecond=0)

                    # Reset transition probability every event
                    event_tp = copy.deepcopy(transition_probability)

                    # Dynamic transition adjustments
                    progress = min(len(cart_content) / max(target_cart_size, 1), 1.0)

                    # Seasonal peak category uplift
                    season, season_type = get_seasonal_event(timestamp)
                    if season and season_type:
                        seasonal_peak = CAMPAIGN_PEAK_CATEGORIES["Seasonal"]
                        if isinstance(seasonal_peak, dict):
                            peak_categories = seasonal_peak.get(season_type, [])
                            if previous_category in peak_categories:
                                event_tp["Product View"]["Add to Cart"] *= 1.2
                                event_tp["Cart View"]["Checkout Start"] *= 1.1

                    # Apply seasonal uplift (payday, weekends, festivals)
                    event_tp = apply_seasonal_uplift(timestamp, event_tp, progress)

                    # Apply promotion uplift (discount driven behaviour)
                    event_tp = apply_promotion_uplift(
                        event_tp,
                        selected_promotions,
                        seen_promotions,
                        seen_promo_types,
                        progress,
                    )

                    # Stock status effect (blocks or boosts conversion)
                    event_tp = apply_stock_status_uplift(
                        ctx, event_tp, online_store_id, previous_product_id, timestamp
                    )

                    # Cart state (non empty carts increases checkout likelihood)
                    if cart_content:
                        event_tp["Home View"]["Cart View"] += 0.05
                        event_tp["Product View"]["Cart View"] += 0.05

                    # Apply mission bias
                    event_tp = apply_mission_bias(
                        event_tp, mission_choice, previous_event_type, progress
                    )

                    # Adjust transition probabilities based on cart progress (with slight boost for essential categories)
                    event_tp = normalise_probability(
                        apply_purchase_progress_bias(
                            event_tp,
                            previous_event_type,
                            previous_category,
                            events,
                            progress,
                        )
                    )

                    # --- Prevent invalid cart actions ---
                    if not cart_content:
                        for e in ["Checkout Start", "Remove from Cart", "Cart View"]:
                            event_tp[previous_event_type].pop(e, None)
                        event_tp = normalise_probability(event_tp)

                    if previous_event_type == "Product View" and previous_event_type:

                        status = get_product_stock_status(
                            ctx, online_store_id, previous_product_id, timestamp
                        )

                        if status not in IN_STOCK_STATUS:
                            event_tp[previous_event_type].pop("Add to Cart", None)
                            event_tp = normalise_probability(event_tp)

                    # --- Next Event Sampling ---
                    # Predetermined event
                    if pending_events:
                        next_action = pending_events.pop(0)
                        event_type = next_action["type"]
                        product_id = next_action.get("product_id", None)
                        if product_id:
                            category = product_category_map.get(product_id, None)
                    else:
                        if previous_event_type not in event_tp:
                            event_type = random.choice(list(event_tp.keys()))
                        else:
                            current_transitions: dict[str, float] = event_tp[
                                previous_event_type
                            ]
                            event_type = random.choices(
                                list(current_transitions.keys()),
                                weights=list(current_transitions.values()),
                            )[0]

                # --- Event Detail Generation ---
                scroll_depth, time_on_page = resolve_scroll_and_time(
                    event_type, mission_choice
                )

                if event_type == "Remove from Cart":
                    product_id, category, product_name, cart_content = (
                        resolve_remove_from_cart(ctx, cart_content)
                    )

                elif event_type == "Add to Cart":
                    product_id, category, product_name, cart_content = (
                        resolve_add_to_cart(
                            ctx,
                            product_id,
                            previous_product_id,
                            previous_category,
                            cart_content,
                            online_store_id,
                            timestamp,
                        )
                    )

                elif event_type == "Product View":
                    product_id, category, product_name, stock_status = (
                        resolve_product_view(
                            ctx,
                            product_id,
                            previous_event_type,
                            previous_category,
                            previous_product_id,
                            previous_search_term,
                            cart_content,
                            customer_segment,
                            session_affinity_categories,
                            online_store_id,
                            timestamp,
                        )
                    )

                elif event_type == "Category View":
                    category = resolve_category_view(
                        previous_category, customer_segment, session_affinity_categories
                    )

                elif event_type == "Search View":
                    search_term = resolve_search_view(
                        ctx, previous_category, session_affinity_categories
                    )

                # Allow partial checkouts
                elif event_type == "Payment Successful":
                    purchased_items, cart_content = resolve_payment_successful(
                        ctx,
                        cart_content,
                        selected_promotions,
                        mission_choice,
                        has_treatment,
                        customer_segment,
                    )

                # Fallback
                if (
                    event_type in ("Product View", "Add to Cart", "Remove from Cart")
                    and not product_id
                ):
                    product_id = random.choice(product_ids)
                    category = product_category_map.get(product_id, None)
                    product_name = product_name_map.get(product_id, None)

                # --- Page Mapping ---
                page = resolve_page(
                    event_type, product_id or "", category or "", search_term or ""
                )

                # --- Promotion Exposure ---
                relevant_promotions = get_relevant_promotion_on_page(
                    ctx,
                    timestamp,
                    event_type,
                    category,
                    product_id,
                    active_campaigns,
                )

                promotion_ids, bundle_ids = process_promotion_exposure(
                    ctx,
                    relevant_promotions,
                    event_type,
                    product_id,
                    seen_promotions,
                    seen_promo_types,
                    selected_promotions,
                    pending_events,
                )

                # Deduplicate lists
                promotion_ids = list(dict.fromkeys(promotion_ids or []))
                bundle_ids = list(dict.fromkeys(bundle_ids or []))

                # --- Record Event Flow ---
                events.append(event_type)

                previous_event = {
                    "event_type": event_type,
                    "category": category,
                    "product_id": product_id,
                    "search_term": search_term,
                    "timestamp": timestamp,
                    "time_on_page": timedelta(seconds=int(time_on_page)),
                    "cart_content": cart_content,
                    "pending_events": pending_events,
                }

                # --- Store Clickstream Record ---
                clickstreams.append(
                    {
                        "clickstream_id": clickstream_id,
                        "session_id": session_id,
                        "customer_id": customer_id,
                        "customer_segment": customer_segment,
                        "campaign_ids": campaign_ids,
                        "has_treatment_campaign": has_treatment,
                        "has_control_campaign": has_control,
                        "device_category": device_category,
                        "referrer": referrer,
                        "location": location,
                        "event_timestamp": timestamp,
                        "event_order": event_order,
                        "event_type": event_type,
                        "page": page,
                        "scroll_depth": scroll_depth,
                        "product_id": product_id,
                        "product_name": product_name,
                        "category": category,
                        "promotion_ids": promotion_ids,
                        "bundle_ids": bundle_ids,
                        "bounce_flag": bounce_flag,
                        "cart_size": len(cart_content),
                        "cart_content": cart_content.copy(),
                        "purchased_items": purchased_items,
                        "stock_status": stock_status,
                    }
                )

                # Increment
                event_order += 1
                total_events += 1

            # -------------------------------
            # Generation: Session Transitions
            # -------------------------------

            session_index += 1
            total_sessions += 1

            # Decide whether customer returns for the next session
            decision = decide_next_activity(
                ctx,
                activity_multiplier,
                customer_id,
                current_time,
                last_active_time,
                signup_date,
                customer_segment,
                cart_content,
            )

            # --- Activity: Churn Path ---
            if decision == "Churn":
                break

            # --- Activity: Inactive Path ---
            elif decision == "Inactive":
                # Sample long inactivity gap
                gap_days = sample_inactive_gap(customer_segment)
                current_time += timedelta(days=gap_days)
                current_time = current_time.replace(microsecond=0)

                reactivation_time = attempt_reactivation(
                    ctx,
                    activity_multiplier,
                    customer_id,
                    current_time,
                    last_active_time,
                    customer_segment,
                    cart_content,
                )

                if reactivation_time is None:
                    break

                # Get reactivation time
                current_time = reactivation_time.replace(microsecond=0)

                # Log last active time upon reactivation
                last_active_time = current_time

                # Update persistent cart with changes made in session
                customer_cart = cart_content.copy()

            # --- Activity: Continue Path ---
            else:
                # Sample short session gap until next session
                gap_hours = sample_session_gap(
                    customer_segment,
                    cart_content,
                    activity_multiplier,
                    current_time,
                    last_active_time,
                )

                # Log last active time
                last_active_time = current_time

                # Generate realistic next session start time for next session within a small forward window
                current_time += timedelta(hours=gap_hours)
                current_time = current_time.replace(microsecond=0)
                window_end = min(
                    current_time + timedelta(days=MAX_LOOK_AHEAD_DAYS),
                    pd.Timestamp(DATA_END_DATE),
                )

                # Applies behavioural biases (weekends, evenings, paydays)
                current_time = generate_timestamp(current_time, window_end)
                current_time = current_time.replace(microsecond=0)

                # Update persistent cart with changes made in session
                customer_cart = cart_content.copy()

            # After every session end, update session time to last active time
            previous_event["timestamp"] = last_active_time

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(clickstreams), "clickstreams_raw.csv")
