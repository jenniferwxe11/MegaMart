from typing import TypedDict


class CampaignRule(TypedDict):
    duration_days: tuple[int, int]
    ab_test_prob: float


AUDIENCE_PERCENTAGE = 1
CONTROL_GROUP_PERCENTAGE = 0.5
ADJECTIVES = ["Mega", "Hot", "Exclusive", "Limited-Time", "Weekly", "Flash", "VIP"]
CAMPAIGN_NAME_SUFFIXES = ["Sale", "Deals", "Offer", "Promotions"]


CAMPAIGN_TYPE_DISTRIBUTION: dict[str, float] = {
    "Acquisition": 0.35,
    "Retention": 0.45,
    "Clearance": 0.2,
}


CAMPAIGN_TYPE_NAMING: dict[str, list[str]] = {
    "Acquisition": ["Welcome", "First Order", "New User"],
    "Retention": ["Loyalty", "Rewards", "Member"],
    "Clearance": ["Stock Clearance", "Last Chance", "Final Offer"],
}


MAX_CHANNELS_PER_CAMPAIGN_TYPE = {
    "Acquisition": 3,
    "Retention": 2,
    "Clearance": 2,
    "Seasonal": 4,
}


CHANNEL_PROB_BY_CAMPAIGN = {
    "Acquisition": {
        "Paid Advertisements": 0.45,
        "Email": 0.2,
        "SMS": 0.15,
        "Push Notifications": 0.1,
        "In-App": 0.1,
    },
    "Retention": {
        "Push Notifications": 0.35,
        "In-App": 0.3,
        "Email": 0.2,
        "Paid Advertisements": 0.15,
    },
    "Clearance": {
        "Push Notifications": 0.6,
        "In-App": 0.4,
    },
    "Seasonal": {
        "Paid Advertisements": 0.5,
        "Email": 0.25,
        "Push Notifications": 0.15,
        "In-App": 0.1,
    },
}


PRIMARY_SEGMENT_BY_CAMPAIGN: dict[str, dict[str, float]] = {
    "Acquisition": {
        "New Customers": 1,
    },
    "Retention": {
        "Active Customers": 0.5,
        "High Spenders": 0.3,
        "Churn Risk Customers": 0.2,
    },
    "Clearance": {
        "Churn Risk Customers": 0.6,
        "Budget Shoppers": 0.4,
    },
    "Seasonal": {
        "Active Customers": 0.4,
        "High Spenders": 0.3,
        "New Customers": 0.2,
        "Budget Shoppers": 0.1,
    },
}


BUDGET_RANGES_BY_CHANNEL = {
    "Push Notifications": (5000, 30000),
    "In-App": (5000, 35000),
    "Email": (10000, 50000),
    "SMS": (20000, 80000),
    "Paid Advertisements": (50000, 180000),
}


BUDGET_MULTIPLIER_BY_CAMPAIGN = {
    "Acquisition": 1.2,
    "Retention": 0.8,
    "Clearance": 0.7,
    "Seasonal": 1.5,
}


ADDITIONAL_CAMPAIGN_RULES: dict[str, CampaignRule] = {
    "Acquisition": {
        "duration_days": (7, 14),
        "ab_test_prob": 0.85,
    },
    "Retention": {
        "duration_days": (14, 30),
        "ab_test_prob": 0.6,
    },
    "Clearance": {
        "duration_days": (30, 60),
        "ab_test_prob": 0.2,
    },
    "Seasonal": {
        "duration_days": (7, 14),
        "ab_test_prob": 0.8,
    },
}


CAMPAIGN_PEAK_CATEGORIES: dict[str, dict[str, list[str]] | list[str]] = {
    "Seasonal": {
        "Cultural Festival": [
            "Snacks",
            "Beverages",
            "Dairy & Eggs",
            "Frozen Food",
            "Fresh Produce",
            "Pantry Staples",
            "Meat & Seafood",
            "Bakery",
            "Rice & Noodles",
            "Home & Living",
        ],
        "Commercial Mega Sale": [
            "Electronics & Appliances",
            "Home & Living",
            "Sports, Travel & Leisure",
        ],
    },
    "Clearance": [
        "Electronics & Appliances",
        "Home & Living",
        "Sports, Travel & Leisure",
    ],
    "Retention": [
        "Snacks",
        "Beverages",
        "Pantry Staples",
        "Personal Care",
        "Household Essentials",
        "Dairy & Eggs",
    ],
    "Acquisition": [
        "Snacks",
        "Beverages",
        "Home & Living",
        "Electronics & Appliances",
    ],
}


PREFIX_CODE = [
    "SAVE",
    "DEAL",
    "MEGA",
    "PROMO",
    "OFFER",
]


SEASON_CODE_MAP = {
    "Chinese New Year": "CNY",
    "Hari Raya Puasa": "HRP",
    "Diwali": "DIW",
    "Christmas": "XMAS",
    "Black Friday": "BF",
    "1111": "11/11",
    "1212": "12/12",
}


CATEGORY_CODE_MAP = {
    "Snacks": "SNACK",
    "Beverages": "BEV",
    "Dairy & Eggs": "DAIRY",
    "Frozen Food": "FROZEN",
    "Fresh Produce": "FRESH",
    "Pantry Staples": "PANTRY",
    "Household Essentials": "ESSEN",
    "Health & Beauty": "HEALTH",
    "Baby Products": "BABY",
    "Canned Goods": "CANNED",
    "Personal Care": "CARE",
    "Meat & Seafood": "MEAT",
    "Bakery": "BAKE",
    "Cleaning Supplies": "CLEAN",
    "Rice & Noodles": "RICE",
    "Breakfast Foods": "BFAST",
    "Electronics & Appliances": "ELEC",
    "Home & Living": "H&L",
    "Sports, Travel & Leisure": "L&R",
}


CHANNEL_CONSENT_MAP = {
    "Email": "email_marketing_opt_in",
    "SMS": "sms_marketing_opt_in",
    "Push Notifications": "push_notifications_opt_in",
}


DIRECT_MESSAGE_CHANNELS = {
    "Email",
    "SMS",
    "Push Notifications",
}


EXPOSURE_ONLY_CHANNELS = {
    "Paid Advertisements",
    "In-App",
}


DIRECT_MESSAGE_CHANNEL_RATE = {
    "Deliver": {
        "Email": 0.95,
        "SMS": 0.98,
        "Push Notifications": 0.9,
    },
    "Open": {
        "Email": 0.25,
        "SMS": 0.15,
        "Push Notifications": 0.35,
    },
    "Click": {
        "Email": 0.1,
        "SMS": 0.05,
        "Push Notifications": 0.15,
    },
}

EXPOSURE_ONLY_CHANNEL_RATES = {
    "Deliver": {
        "Paid Advertisements": 0.85,
        "In-App": 0.95,
    },
    "Click": {
        "Paid Advertisements": 0.02,
        "In-App": 0.08,
    },
}


COST_PER_MSG = {
    "Email": 0.02,
    "Push Notifications": 0.01,
    "SMS": 0.05,
    "In-App": 0.0,
    "Paid Advertisements": 1.0,
}
