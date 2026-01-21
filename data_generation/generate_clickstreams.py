import random
import uuid
from datetime import datetime, timedelta
import re
import copy

import numpy as np
import pandas as pd
from config import (
    BRANDS,
    CAMPAIGN_SESSION_FREQUENCY,
    CART_SIZE_BY_SEGMENT,
    CATEGORIES,
    CATEGORY_FREQUENCY,
    CATEGORY_ITEMS,
    DAY_WEIGHTS,
    HOUR_WEIGHTS,
    LANDING_PAGE_BEHAVIOUR,
    MAX_SESSIONS,
    NUM_CLICKSTREAMS,
    PARETO_ALPHA,
    PAYDAY_BOOST,
    REFERRER_DISTRIBUTION,
    SEASON_PEAK_CATEGORIES,
    SEASONAL_DATES,
    SEASONAL_UPLIFT,
    SEGMENT_CATEGORY_BIAS,
    SEGMENT_SESSION_FREQUENCY,
    TIME_ON_PAGE,
    VALID_EVENT_TRANSITIONS,
)
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

clickstreams = []
clickstream_ids = []

customers_df = pd.read_csv("data_generation/raw_data/customers_raw.csv")
# only choose customer types from online only and omnichannel
customer_ids = (
    customers_df[customers_df["customer_type"].isin(["Online Only", "Omnichannel"])][
        "customer_id"
    ]
    .dropna()
    .tolist()
)

products_df = pd.read_csv("data_generation/raw_data/products_raw.csv")
product_ids = products_df["product_id"].dropna().tolist()
products_df.loc[:,"stock_quantity"] = pd.to_numeric(products_df["stock_quantity"], errors="coerce")

# ensure columns exist and are datetime type
products_df.loc[:, "promotion_start_date"] = pd.to_datetime(
    products_df.get("promotion_start_date"), errors="coerce"
)
products_df.loc[:, "promotion_end_date"] = pd.to_datetime(
    products_df.get("promotion_end_date"), errors="coerce"
)

campaigns_df = pd.read_csv("data_generation/raw_data/campaigns_raw.csv")
campaign_ids = campaigns_df["campaign_id"].dropna().tolist()

campaign_assignments_df = pd.read_csv(
    "data_generation/raw_data/campaign_assignments_raw.csv"
)

region_area_df = pd.read_csv("data_generation/raw_data/region_areas.csv")

LOCATIONS = region_area_df["area"].tolist()


SEARCH_TERMS = []
SEARCH_TERMS.extend(CATEGORIES)
for brand_list in BRANDS.values():
    SEARCH_TERMS.extend(brand_list)
for item_list in CATEGORY_ITEMS.values():
    SEARCH_TERMS.extend(item_list)

def pareto_capped(alpha, cap):
    value = np.random.pareto(alpha) + 1
    value = int(np.clip(value,1,cap))
    return value


def generate_timestamp(start_date, end_date):
    # Define the start and end date range
    start = max(datetime(2024, 1, 1), start_date)
    end = min(datetime(2024, 12, 31), end_date)

    # Generate all possible dates in the range
    all_dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]

    # Assign weights based on weekend/weekday and payday boosts
    date_weights = []
    for d in all_dates:
        w = 1.0
        if d.weekday() >= 5:  # Saturday=5, Sunday=6
            w *= DAY_WEIGHTS.get("Weekend", 1.0)
        else:
            w *= DAY_WEIGHTS.get("Weekday", 1.0)
        if d.day in (1, 15):
            w *= PAYDAY_BOOST
        date_weights.append(w)

    # Pick a date with weighted probability
    date = random.choices(all_dates, weights=date_weights, k=1)[0]

    # Pick hour based on HOUR_WEIGHTS
    r = random.random()
    cumulative_weight = 0.0
    hour = 12  # default fallback
    total_weight = sum(weight for _, (_, _, weight) in HOUR_WEIGHTS.items())

    for _, (hour_start, hour_end, weight) in HOUR_WEIGHTS.items():
        cumulative_weight += weight / total_weight  # normalize to 1
        if r <= cumulative_weight:
            hour = random.randint(hour_start, hour_end - 1)
            break

    # Pick random minute and second
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    timestamp = datetime(date.year, date.month, date.day, hour, minute, second)
    return timestamp


def generate_scroll_depth():
    # base skew toward shallow scrolls
    base = (random.random() ** 2) * 100

    if base < 15:
        return random.randint(0, 15)

    elif base < 30:
        return random.choices([20, 25, 30], weights=[0.3, 0.4, 0.3], k=1)[0]

    elif base < 50:
        return random.choices([40, 50], weights=[0.4, 0.6], k=1)[0]

    elif base < 75:
        return random.choices([60, 75], weights=[0.5, 0.5], k=1)[0]

    else:
        return random.choices([85, 90, 100], weights=[0.3, 0.3, 0.4], k=1)[0]


def get_category(customer_segment):
    assert CATEGORY_FREQUENCY, "CATEGORY_FREQUENCY must not be empty"
    base = CATEGORY_FREQUENCY.copy()
    segment_bias = SEGMENT_CATEGORY_BIAS.get(customer_segment, {})

    adjusted_weights = {}

    # active customers and churn risk customers have equal preference for all categories
    for category, frequency in base.items():
        bias_multiplier = segment_bias.get(category, 1.0)
        adjusted_weights[category] = frequency * bias_multiplier

    category = random.choices(
        list(adjusted_weights.keys()), weights=list(adjusted_weights.values()), k=1
    )[0]

    return category


def get_random_product_from_search_term(search_term):
    term = search_term.replace("+", " ").strip()
    term = re.escape(term) 
    product_ids = products_df[
        products_df["product_name"].str.contains(
            term,
            case=False,  # case-insensitive
            na=False,  # missing names won’t crash
            regex=True,  # allows partial matches
        )
    ]["product_id"].tolist()
    if product_ids:
        return random.choice(product_ids)
    return None


def get_random_product_from_category(category):
    product_ids = (
        products_df[products_df["category"] == category]["product_id"].dropna().tolist()
    )
    if product_ids:
        return random.choice(product_ids)
    return None


def get_category_from_product(product_id):
    return products_df.loc[products_df["product_id"]==product_id, "category"].iloc[0]

def get_product_name(product_id):
    return products_df.loc[products_df["product_id"]==product_id, "product_name"].iloc[0]


def is_in_stock(product_id):
    product_row = products_df[products_df["product_id"] == product_id].iloc[0]
    return product_row["stock_quantity"] > 0


def initialize_cart(customer_segment, campaign_group, max_items=10, max_attempts=20):
    lam = CART_SIZE_BY_SEGMENT.get(customer_segment, 1)
    initialized_cart_size = np.random.poisson(lam)

    if campaign_group == "treatment":
        initialized_cart_size += np.random.poisson(1)

    initialized_cart_size = min(initialized_cart_size, max_items)
    cart_content = []
    attempts = 0

    while len(cart_content) < initialized_cart_size and attempts < max_attempts:
        category = get_category(customer_segment)
        product_id = get_random_product_from_category(category)
        attempts += 1

        if product_id and is_in_stock(product_id) and product_id not in cart_content:
            cart_content.append(product_id)

    return cart_content


def get_time_of_day(timestamp):
    if 18 <= timestamp.hour < 22:
        return "Evening"
    return "Daytime"


def get_day_type(timestamp):
    if timestamp.weekday() >= 5:
        return "Weekend"
    return "Weekday"


def get_pay_cycle(timestamp):
    if timestamp.day in [1, 15]:
        return "Payday"
    elif timestamp.day in [28, 29, 30, 31, 1, 2]:
        return "Payday spillover"
    return None


def get_seasonal_event(timestamp):
    for season, (start, end) in SEASONAL_DATES.items():
        if start <= timestamp <= end:
            return season
    return None


def apply_seasonal_uplift(timestamp, transition_probability):
    extra_events = 0

    time_of_day = get_time_of_day(timestamp)
    day_type = get_day_type(timestamp)
    pay_cycle = get_pay_cycle(timestamp)
    season = get_seasonal_event(timestamp)

    for s in [time_of_day, day_type, pay_cycle, season]:
        if s:
            # seasonal event uplift
            min_event, max_event = SEASONAL_UPLIFT[s].get("extra_events", (0, 0))
            extra_events += random.randint(min_event, max_event)

            # seasonal increase for atc uplift
            low_atc, high_atc = SEASONAL_UPLIFT[s].get("atc_mult", (0, 0))
            atc_multiplier = random.uniform(low_atc, high_atc)
            transition_probability["Product View"]["Add to Cart"] *= atc_multiplier

            # seasonal increase for checkout uplift
            low_checkout, high_checkout = SEASONAL_UPLIFT[s].get(
                "checkout_mult", (0, 0)
            )
            checkout_multiplier = random.uniform(low_checkout, high_checkout)
            transition_probability["Cart View"]["Checkout Start"] *= checkout_multiplier

            # seasonal increase for conversion uplift
            low_conversion, high_conversion = SEASONAL_UPLIFT[s].get(
                "conversion_mult", (0, 0)
            )
            conversion_multiplier = random.uniform(low_conversion, high_conversion)
            transition_probability["Checkout Start"][
                "Payment Attempt"
            ] *= conversion_multiplier

    return extra_events, transition_probability


def normalise_probability(transition_probability):
    for event, transitions in transition_probability.items():
        total = sum(transitions.values())
        if total > 0:
            normalized_transitions = {}
            for next_event, prob in transitions.items():
                normalized_transitions[next_event] = prob / total
            transition_probability[event] = normalized_transitions
    return transition_probability


def get_transition_probability(
    customer_segment,
    campaign_group,
    timestamp,
    cart_content,
):
    transition_probability = copy.deepcopy(VALID_EVENT_TRANSITIONS)
    extra_events = 0

    if campaign_group == "treatment":

        # increase ATC rate for treatment group
        transition_probability["Product View"]["Add to Cart"] *= 1.1

        # increase checkout uplift for treatment group
        transition_probability["Cart View"]["Checkout Start"] *= 1.1

        # increase conversion uplift for treatment group
        transition_probability["Checkout Start"]["Payment Attempt"] *= 1.1

        extra_events = random.randint(2, 5)

    # increase ATC rate for High Spenders
    if customer_segment == "High Spenders":
        transition_probability["Product View"]["Add to Cart"] *= 1.1

    # increase Cart View rate if cart is not empty
    if cart_content:
        transition_probability["Home View"]["Cart View"] += 0.05
        transition_probability["Product View"]["Cart View"] += 0.05

    extra_events, transition_probability = apply_seasonal_uplift(
        timestamp, transition_probability
    )

    return extra_events, transition_probability


def get_next_event_type(previous_event_type, transition_probability, cart_content):
    next_event_type = None
    while next_event_type is None:
        next_event_type = random.choices(
            list(transition_probability.get(previous_event_type, None).keys()),
            weights=list(transition_probability.get(previous_event_type, None).values()),
            k=1,
        )[0]
        # ensure cart related events only occur when cart is not empty
        if (
            next_event_type in ("Remove from Cart", "Cart View", "Checkout Start")
            and not cart_content
        ):
            next_event_type = None
    return next_event_type


def get_search_term():
    assert SEARCH_TERMS, "SEARCH_TERMS must not be empty"
    if random.random() < 0.2:
        return fake.word().lower().replace(" ", "+")
    search_term = random.choice(SEARCH_TERMS)
    words = search_term.split()
    term_length = random.randint(1, min(2, len(words)))
    start_index = random.randint(0, len(words) - term_length)
    return (
        " ".join(words[start_index : start_index + term_length])
        .replace(" ", "+")
        .replace("&", "")
    )


def get_location(customer_id):
    customer_row = customers_df[customers_df["customer_id"] == customer_id]
    if customer_row.empty:
        return random.choice(LOCATIONS)

    r = random.random()
    if r < 0.8:
        area = customer_row.iloc[0]["area"]
    elif r < 0.95:
        region = customer_row.iloc[0]["region"]
        area_choices = region_area_df[region_area_df["region"] == region][
            "area"
        ].tolist()
        area = random.choice(area_choices)
    else:
        area = random.choice(LOCATIONS)
    return area


total_events = 0
for customer_id in customer_ids:
    if total_events >= NUM_CLICKSTREAMS:
        break
    customer_row = customers_df[customers_df["customer_id"] == customer_id]
    customer_segment = customer_row["customer_segment"].iloc[0]
    signup_date = pd.to_datetime(customer_row["signup_date"].iloc[0])

    campaign_group = None
    session_start_time = None

    customer_campaigns = campaign_assignments_df[
        campaign_assignments_df["customer_id"] == customer_id
    ]
    
    # determine number of sessions this customer will have
    num_sessions = pareto_capped(PARETO_ALPHA, MAX_SESSIONS) * SEGMENT_SESSION_FREQUENCY.get(customer_segment, 1.0) * CAMPAIGN_SESSION_FREQUENCY.get(campaign_group, 1.0)
    num_sessions = int(np.clip(num_sessions,1,MAX_SESSIONS))

    for session_index in range(num_sessions):
        if total_events >= NUM_CLICKSTREAMS:
            break

        session_id = str(uuid.uuid4())

        if not customer_campaigns.empty:
            campaign_row = customer_campaigns.sample(1).iloc[0]
            campaign_id = campaign_row["campaign_id"]
            campaign_assignments_row = campaign_assignments_df[
                campaign_assignments_df["campaign_id"] == campaign_id
            ]
            campaign_group = campaign_assignments_row["group"].iloc[0]

            campaign_row = campaigns_df[campaigns_df["campaign_id"] == campaign_id]
            campaign_start_date = pd.to_datetime(campaign_row["start_date"].iloc[0])
            campaign_end_date = pd.to_datetime(campaign_row["end_date"].iloc[0])
            session_start_time = generate_timestamp(campaign_start_date, campaign_end_date)
            session_start_time = session_start_time.replace(microsecond=0)
        else:
            campaign_id = None
            campaign_group = "non-campaign"
            session_start_time = generate_timestamp(signup_date, datetime(2024, 12, 31))
            session_start_time = session_start_time.replace(microsecond=0)

        # initialize cart content
        cart_content = initialize_cart(customer_segment, campaign_group)

        location = get_location(customer_id)

        device_type = random.choices(
            ["Mobile", "Desktop", "Tablet"], weights=[0.8, 0.15, 0.05], k=1
        )[0]

        referrer = random.choices(
            list(REFERRER_DISTRIBUTION.keys()),
            weights=list(REFERRER_DISTRIBUTION.values()),
            k=1,
        )[0]

        landing_behaviour = LANDING_PAGE_BEHAVIOUR.get(referrer, None)

        if landing_behaviour is None:
            # safe fallback (direct traffic default)
            landing_behaviour = LANDING_PAGE_BEHAVIOUR["direct"]

        landing_page_type = random.choices(
            list(landing_behaviour.keys()),
            weights=list(landing_behaviour.values()),
            k=1,
        )[0]

        # change transition probability according to segment, campaign group, seasonal events, and cart content
        extra_events, transition_probability = get_transition_probability(
            customer_segment=customer_segment,
            campaign_group=campaign_group,
            timestamp=session_start_time,
            cart_content=cart_content,
        )

        # normalise transition probability
        transition_probability = normalise_probability(transition_probability)

        # determine number of events in this session
        event_count = random.randint(3,15)
        event_count += extra_events

        bounce_flag = 1 if event_count == 1 else 0
        event_order = 1

        previous_event = {
            "event_type": None,
            "category": None,
            "product_id": None,
            "search_term": None,
            "timestamp": None,
            "time_on_page": None,
            "cart_content": cart_content,
        }

        events = []

        for event_index in range(event_count):
            # reset transition probability every event
            event_transition_probability = copy.deepcopy(transition_probability)

            clickstream_id = f"{session_id}_{event_index}"
            clickstream_ids.append(clickstream_id)

            # get previous event details
            previous_event_type = previous_event.get("event_type", None)
            previous_category = previous_event.get("category", None)
            previous_product_id = previous_event.get("product_id", None)
            previous_search_term = previous_event.get("search_term","")
            previous_timestamp = previous_event.get("timestamp", None)
            previous_time_on_page = previous_event.get("time_on_page", None)

            # initialise current event details
            event_type = None
            category = None
            product_id = None
            product_name = None
            search_term = None
            timestamp = None
            time_on_page = None
            purchased_items = []
            cart_content = previous_event.get("cart_content", []).copy()

            scroll_depth = None

            if event_order == 1:
                event_type = landing_page_type
                # introduce delay after session start time
                timestamp = session_start_time + timedelta(seconds=random.randint(1, 300))
                timestamp = timestamp.replace(microsecond=0)

            else:
                assert previous_timestamp is not None
                assert previous_time_on_page is not None

                # event timestamp based on previous event time on page with idle time
                timestamp = previous_timestamp + previous_time_on_page + timedelta(seconds=random.randint(5, 180))
                timestamp = timestamp.replace(microsecond=0)

                # seasonal peak category uplift
                season = get_seasonal_event(timestamp)
                if season:
                    peak_categories = SEASON_PEAK_CATEGORIES[season]
                    if category in peak_categories:
                        event_transition_probability["Product View"]["Add to Cart"] *= 1.2
                        event_transition_probability["Cart View"]["Checkout Start"] *= 1.1

                # normalise probabilities
                event_transition_probability = normalise_probability(
                    event_transition_probability
                )

                # determine next event
                event_type = get_next_event_type(
                    previous_event_type,
                    event_transition_probability,
                    cart_content,
                )

            if event_type in ("Home View", "Search View", "Category View", "Product View"):
                # scroll_depth skewed to shallow
                scroll_depth = generate_scroll_depth()
                # time on page affected by scroll depth
                low, mode, high = TIME_ON_PAGE.get(event_type, (3, 8, 25))
                time_on_page = random.triangular(low, high, mode) * (
                    0.8 + (scroll_depth / 100) * 0.6
                )
            else:
                # no scroll_depth
                low, mode, high = TIME_ON_PAGE.get(event_type, (3, 8, 25))
                time_on_page = random.triangular(low, high, mode)

            ###############################################

            valid_event_chosen = False
            max_attempts = 5
            attempt = 0

            # ensure that event chosen is valid
            while not valid_event_chosen and attempt < max_attempts:
                attempt += 1

                if event_type == "Checkout Start":
                    if (not cart_content) or ("Add to Cart" not in events):
                        event_transition_probability[previous_event_type].pop(
                            "Checkout Start", None
                        )
                        event_transition_probability = normalise_probability(
                            event_transition_probability
                        )
                        event_type = get_next_event_type(
                            previous_event_type,
                            event_transition_probability,
                            cart_content,
                        )
                        # retry
                        continue

                elif event_type == "Remove from Cart":
                    if cart_content:
                        product_id = random.choice(cart_content)
                        category = get_category_from_product(product_id)
                        product_name = get_product_name(product_id)
                        cart_content.remove(product_id)
                    else:
                        # choose another event
                        event_transition_probability[previous_event_type].pop(
                            "Remove from Cart", None
                        )
                        event_transition_probability = normalise_probability(
                            event_transition_probability
                        )
                        event_type = get_next_event_type(
                            previous_event_type,
                            event_transition_probability,
                            cart_content,
                        )
                        # retry
                        continue

                elif event_type == "Add to Cart":
                    # Try to add the product from previous Product View
                    if previous_product_id and is_in_stock(previous_product_id):
                        cart_content.append(previous_product_id)
                        product_id = previous_product_id
                        category = get_category_from_product(product_id)
                        product_name = get_product_name(product_id)
                    else:
                        event_type = get_next_event_type(
                            previous_event_type,
                            event_transition_probability,
                            cart_content,
                        )
                        # retry
                        continue

                valid_event_chosen = True

            # events that dont need to be validated
            if event_type == "Product View":
                # get category and product id
                if previous_event_type == "Category View" and previous_category:
                    category = previous_category
                    product_id = get_random_product_from_category(category)
                    product_name = get_product_name(product_id)
                elif previous_event_type == "Search View" and previous_search_term:
                    product_id = get_random_product_from_search_term(previous_search_term)
                    if product_id:
                        category = get_category_from_product(product_id)
                    else:
                        # simulate user clicking on random products when search returns no results
                        product_id = random.choice(product_ids)
                        category = get_category_from_product(product_id)
                else:
                    category = get_category(customer_segment)
                    product_id = get_random_product_from_category(category)

                # fallback
                if not product_id:
                    product_id = random.choice(product_ids)
                    category = get_category_from_product(product_id)

            elif event_type == "Category View":
                # category selection according to customer segment
                category = get_category(customer_segment)

            elif event_type == "Search View":
                # get search term
                search_term = get_search_term()

            ##################################################
            # record event flow
            events.append(event_type)
            
            # allow partial checkouts
            if event_type == "Payment Successful":
                purchase_count = random.randint(1, len(cart_content))
                purchased_items = random.sample(cart_content, purchase_count)
                for item in purchased_items:
                    cart_content.remove(item)

            EVENT_PAGE_MAPPING = {
                "Home View": "/home",
                "Category View": "/category/{category}",
                "Search View": "/search?q={search_term}",
                "Product View": "/product/{product_id}",
                "Add to Cart": "/add_to_cart/{product_id}",
                "Cart View": "/cart",
                "Remove from Cart": "/remove_from_cart/{product_id}",
                "Checkout Start": "/checkout",
                "Payment Attempt": "/payment",
                "Payment Successful": "/payment/success",
                "Payment Failed": "/payment/fail",
            }

            page_template = EVENT_PAGE_MAPPING.get(event_type, "")

            if page_template:
                if "{product_id}" in page_template and product_id is not None:
                    page = page_template.format(product_id=product_id)
                elif "{category}" in page_template and category is not None:
                    page = page_template.format(category=category.replace(" ", "-").lower())
                elif "{search_term}" in page_template and search_term is not None:
                    page = page_template.format(search_term=search_term)
                else:
                    page = page_template

            previous_event = {
                "event_type": event_type,
                "category": category,
                "product_id": product_id,
                "search_term": search_term,
                "timestamp": timestamp,
                "time_on_page": timedelta(seconds=int(time_on_page)),
                "cart_content": cart_content,
            }

            clickstreams.append(
                {
                    "clickstream_id": clickstream_id,
                    "session_id": session_id,
                    "customer_id": customer_id,
                    "customer_segment": customer_segment,
                    "campaign_id": campaign_id,
                    "campaign_group": campaign_group,
                    "device_type": device_type,
                    "referrer": referrer,
                    "location": location,
                    "timestamp": timestamp,
                    "event_order": event_order,
                    "event_type": event_type,
                    "page": page,
                    "scroll_depth": scroll_depth,
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "bounce_flag": bounce_flag,
                    "cart_size": len(cart_content),
                    "cart_content": cart_content.copy(),
                    "purchased_items": purchased_items,
                }
            )

            # reset values
            # scroll depth
            scroll_depth = None
            # product information
            product_id = None
            product_name = None
            category = None
            purchased_items = []

            # increment
            event_order += 1
            total_events += 1

df_clickstreams = pd.DataFrame(clickstreams)
df_clickstreams.to_csv("data_generation/raw_data/clickstreams_raw.csv", index=False)
print("clickstreams_raw.csv file generated")
