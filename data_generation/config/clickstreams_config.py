from typing import Any

FIRST_SESSION_WINDOW_DAYS = 7
MAX_ACTIVITY_MULTIPLIER = 10
MAX_LOOK_AHEAD_DAYS = 3
PARETO_ALPHA = 2.0
IN_STOCK_STATUS = (
    "Low Stock",
    "Limited Stock",
    "In Stock",
    "Overstock",
    "Unknown",
)  # to do

RETURN_PROB_BY_SEGMENT = {
    "New Customers": 0.7,  # Many new users try once/twice, some come back
    "Active Customers": 0.65,  # Usually return frequently
    "High Spenders": 0.75,  # Very loyal, high probability to return
    "Budget Shoppers": 0.55,  # Ooccasional visits, lower probability
    "Churn Risk Customers": 0.4,  # Likely to churn early
}


REACTIVATION_BY_SEGMENT = {
    "New Customers": 0.07,
    "Active Customers": 0.1,
    "High Spenders": 0.15,
    "Budget Shoppers": 0.08,
    "Churn Risk Customers": 0.05,
}


SEASONAL_REACTIVATION_BOOST = {
    # High-intent sale events (strong spikes)
    "1111": 2.5,
    "1212": 2.5,
    "Black Friday": 2.2,
    # Moderate commercial events
    "Christmas": 1.6,
    # Cultural (planned shopping, less impulsive)
    "Chinese New Year": 1.4,
    "Hari Raya Puasa": 1.3,
    "Diwali": 1.3,
}


SESSION_GAP_SCALE_BY_SEGMENT = {
    "New Customers": 36,  # Exploring but not yet habitual (~ 1.5 days)
    "Active Customers": 24,  # Regular (~ daily)
    "High Spenders": 12,  # Very frequent (~ twice a day)
    "Budget Shoppers": 48,  # More deliberate (~ every 2 days)
    "Churn Risk Customers": 96,  # Infrequent (~ every 4 days)
}


PROMOTION_TYPE_MULTIPLIER = {
    "free_shipping": {
        "atc_multiplier": (1.00, 1.10),
        "checkout_multiplier": (1.05, 1.15),
        "remove_multiplier": (0.7, 0.9),
        "stackable": True,
    },
    "dollar_discount": {
        "atc_multiplier": (1.05, 1.20),
        "checkout_multiplier": (1.05, 1.15),
        "remove_multiplier": (0.7, 0.9),
        "stackable": False,
        "priority": 1,
    },
    "percentage_discount": {
        "atc_multiplier": (1.10, 1.30),
        "checkout_multiplier": (1.10, 1.25),
        "remove_multiplier": (0.6, 0.85),
        "stackable": False,
        "priority": 2,
    },
    "bundle": {
        "atc_multiplier": (1.10, 1.25),
        "checkout_multiplier": (1.05, 1.15),
        "remove_multiplier": (0.6, 0.8),
        "stackable": True,
    },
}


CATEGORY_EXPOSURE_MULTIPLIER = {
    "Snacks": 1.4,
    "Beverages": 1.3,
    "Dairy & Eggs": 1.2,
    "Frozen Food": 1.1,
    "Health & Beauty": 1.1,
    "Canned Goods": 1.0,
    "Meat & Seafood": 1.0,
    "Personal Care": 1.0,
    "Electronics & Appliances": 0.9,
    "Home & Living": 0.9,
    "Fresh Produce": 0.8,
    "Bakery": 0.7,
    "Breakfast Foods": 0.6,
}


CATEGORY_DEMAND_DISTRIBUTION = {
    "Snacks": 0.09,
    "Beverages": 0.07,
    "Dairy & Eggs": 0.11,
    "Frozen Food": 0.05,
    "Fresh Produce": 0.14,
    "Pantry Staples": 0.10,
    "Household Essentials": 0.04,
    "Health & Beauty": 0.04,
    "Baby Products": 0.02,
    "Canned Goods": 0.03,
    "Personal Care": 0.04,
    "Meat & Seafood": 0.05,
    "Bakery": 0.03,
    "Cleaning Supplies": 0.04,
    "Rice & Noodles": 0.05,
    "Breakfast Foods": 0.05,
    "Electronics & Appliances": 0.02,
    "Home & Living": 0.04,
    "Sports, Travel & Leisure": 0.04,
}


DAY_WEIGHTS = {
    "Weekday": 1.0,
    "Weekend": 1.3,
    "Payday": 1.4,
    "Payday Spillover": 1.15,
}


HOUR_WEIGHTS = {
    "Late Night": (0, 5, 0.05),  # 12am-5am
    "Early Morning": (5, 8, 0.08),  # 5am-8am
    "Morning": (8, 12, 0.20),  # 8am-12pm
    "Afternoon": (12, 17, 0.25),  # 12pm-5pm
    "Evening": (17, 21, 0.30),  # 5pm-9pm
    "Night": (21, 24, 0.12),  # 9pm-12am
}


LANDING_PAGE_BEHAVIOUR = {
    "organic_search": {"Home View": 0.4, "Search View": 0.4, "Product View": 0.2},
    "direct": {"Home View": 0.6, "Category View": 0.2, "Product View": 0.2},
    "social_media": {"Home View": 0.5, "Product View": 0.3, "Category View": 0.2},
    "email": {"Home View": 0.3, "Product View": 0.4, "Category View": 0.3},
    "unknown": {
        "Home View": 0.3,
        "Product View": 0.3,
        "Category View": 0.2,
        "Search View": 0.2,
    },
}


REFERRER_DISTRIBUTION = {
    "organic_search": 0.35,
    "direct": 0.25,
    "social_media": 0.2,
    "email": 0.15,
    "unknown": 0.05,
}


SEASONAL_UPLIFT: dict[str, dict[str, Any]] = {
    "Daytime": {
        "extra_events": (0, 1),
        "atc_mult": (0.98, 1.02),
        "checkout_mult": (0.98, 1.02),
        "conversion_mult": (0.98, 1.02),
    },
    "Evening": {
        "extra_events": (1, 3),
        "atc_mult": (1.1, 1.2),
        "checkout_mult": (1.05, 1.15),
        "conversion_mult": (1.05, 1.12),
    },
    "Weekday": {
        "extra_events": (0, 1),
        "atc_mult": (1.02, 1.08),
        "checkout_mult": (1.08, 1.12),
        "conversion_mult": (1.08, 1.02),
    },
    "Weekend": {
        "extra_events": (1, 3),
        "atc_mult": (1.1, 1.2),
        "checkout_mult": (1.08, 1.15),
        "conversion_mult": (1.1, 1.18),
    },
    "Payday": {
        "extra_events": (2, 4),
        "atc_mult": (1.2, 1.4),
        "checkout_mult": (1.15, 1.3),
        "conversion_mult": (1.15, 1.3),
    },
    "Payday Spillover": {
        "extra_events": (1, 3),
        "atc_mult": (1.1, 1.2),
        "checkout_mult": (1.08, 1.15),
        "conversion_mult": (1.1, 1.18),
    },
    "CNY": {
        "extra_events": (3, 6),
        "atc_mult": (1.2, 1.4),
        "checkout_mult": (1.3, 1.6),
        "conversion_mult": (1.5, 2.2),
    },
    "Hari Raya Puasa": {
        "extra_events": (2, 5),
        "atc_mult": (1.15, 1.3),
        "checkout_mult": (1.2, 1.4),
        "conversion_mult": (1.3, 2.0),
    },
    "Diwali": {
        "extra_events": (2, 5),
        "atc_mult": (1.15, 1.3),
        "checkout_mult": (1.2, 1.4),
        "conversion_mult": (1.3, 2.0),
    },
    "Christmas": {
        "extra_events": (3, 6),
        "atc_mult": (1.25, 1.5),
        "checkout_mult": (1.4, 1.8),
        "conversion_mult": (1.6, 2.5),
    },
    "1111": {
        "extra_events": (5, 10),
        "atc_mult": (1.5, 2),
        "checkout_mult": (1.8, 2.5),
        "conversion_mult": (2, 3.5),
    },
    "1212": {
        "extra_events": (5, 10),
        "atc_mult": (1.5, 2),
        "checkout_mult": (1.8, 2.5),
        "conversion_mult": (2, 3.5),
    },
    "Black Friday": {
        "extra_events": (5, 10),
        "atc_mult": (1.5, 2.5),
        "checkout_mult": (2, 3),
        "conversion_mult": (2.5, 4),
    },
}


MISSION_SCROLL_BIAS = {
    "Quick Top Up": 1.5,
    "Regular Buy": 1.0,
    "Bulk Buy": 0.5,
    "Browsing": 0.3,
}


SEGMENT_MISSION_BIAS = {
    "New Customers": {
        "Quick Top Up": 0.3,
        "Regular Buy": 0.6,
        "Bulk Buy": 0.1,
        "Browsing": 0.0,
    },
    "Active Customers": {
        "Quick Top Up": 0.1,
        "Regular Buy": 0.6,
        "Bulk Buy": 0.3,
        "Browsing": 0.0,
    },
    "Churn Risk Customers": {
        "Quick Top Up": 0.5,
        "Regular Buy": 0.4,
        "Bulk Buy": 0.0,
        "Browsing": 0.1,
    },
    "High Spenders": {
        "Quick Top Up": 0.0,
        "Regular Buy": 0.3,
        "Bulk Buy": 0.7,
        "Browsing": 0.0,
    },
    "Budget Shoppers": {
        "Quick Top Up": 0.1,
        "Regular Buy": 0.4,
        "Bulk Buy": 0.5,
        "Browsing": 0.0,
    },
}

# PERSONAS = {
#     "mission_buyer": 0.25,
#     "browser": 0.3,
#     "indecisive": 0.2,
#     "impulse": 0.15,
#     "distracted": 0.1
# }


SESSION_MISSION_TARGET_RANGE = {
    "Quick Top Up": (1, 5),
    "Regular Buy": (6, 15),
    "Bulk Buy": (16, 40),
    "Browsing": (0, 2),
}


MISSION_EFFICIENCY = {
    "Quick Top Up": (0.8, 1.0),
    "Regular Buy": (0.5, 0.9),
    "Bulk Buy": (0.7, 1.0),
    "Browsing": (0.2, 0.5),
}


MISSION_TRANSITION_MULTIPLIERS = {
    "Quick Top Up": {
        "Add to Cart": 1.2,
    },
    "Regular Buy": {
        "Search View": 1.3,
        "Add to Cart": 1.1,
        "Checkout Start": 1.1,  # 1.5
    },
    "Bulk Buy": {
        "Add to Cart": 1.5,
        "Checkout Start": 1.3,
    },
    "Browsing": {
        "Search View": 1.2,
        "Category View": 1.4,
        "Product View": 1.5,
        "Add to Cart": 0.6,
    },
    # "Indecisive": {
    #     "Product View": 1.8,
    #     "Cart View": 1.2
    # },
    # "Impulse": {
    #     "Add to Cart": 1.8,
    # },
    # "Distracted": {
    #     "Home View": 1.5
    # }
}


MISSION_MAX_MULTIPLIER = {
    "Bulk Buy": 1.8,
    "Regular Buy": 1.5,
    "Quick Top Up": 1.3,
    "Browsing": 1.2,
}


TIME_ON_PAGE = {
    "Home View": (5, 30, 60),
    "Category View": (10, 45, 90),
    "Search View": (5, 20, 45),
    "Product View": (15, 60, 180),
    "Cart View": (10, 30, 60),
    "Add to Cart": (2, 5, 10),
    "Checkout Start": (10, 30, 90),
    "Payment Attempt": (5, 15, 30),
    "Payment Successful": (3, 5, 10),
    "Payment Failed": (3, 5, 15),
    "Remove from Cart": (2, 5, 10),
}


VALID_EVENT_TRANSITIONS: dict[str, dict[str, float]] = {
    "Home View": {
        "Product View": 0.4,
        "Category View": 0.3,
        "Search View": 0.25,
        "Cart View": 0.05,
    },
    "Category View": {
        "Product View": 0.45,
        "Search View": 0.2,
        "Category View": 0.15,
        "Home View": 0.1,
        "Cart View": 0.1,
    },
    "Search View": {
        "Product View": 0.5,
        "Category View": 0.2,
        "Search View": 0.15,
        "Home View": 0.1,
        "Cart View": 0.05,
    },
    "Product View": {
        "Add to Cart": 0.25,
        "Category View": 0.2,
        "Search View": 0.15,
        "Home View": 0.15,
        "Product View": 0.15,
        "Cart View": 0.1,
    },
    "Add to Cart": {
        "Cart View": 0.4,
        "Product View": 0.3,
        "Category View": 0.2,
        "Home View": 0.1,
    },
    "Cart View": {
        "Checkout Start": 0.35,
        "Product View": 0.25,
        "Remove from Cart": 0.15,
        "Home View": 0.15,
        "Category View": 0.1,
    },
    "Remove from Cart": {
        "Cart View": 0.5,
        "Product View": 0.3,
        "Home View": 0.2,
    },
    "Checkout Start": {
        "Payment Attempt": 0.7,
        "Cart View": 0.2,
        "Home View": 0.1,
    },
    "Payment Attempt": {
        "Payment Successful": 0.9,
        "Payment Failed": 0.1,
    },
    "Payment Successful": {"Home View": 0.6, "Category View": 0.4},
    "Payment Failed": {
        "Payment Attempt": 0.5,
        "Cart View": 0.3,
        "Home View": 0.2,
    },
}


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
