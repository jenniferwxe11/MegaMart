from typing import TypedDict


class PaymentMethodConfig(TypedDict):
    methods: list[str]
    weights: list[float]


SESSION_MISSION_TARGET_RANGE = {
    "Quick Top Up": (1, 5),
    "Regular Buy": (6, 15),
    "Bulk Buy": (16, 40),
    "Browsing": (1, 2),
}

CUSTOMER_TYPE_DISTRIBUTION = {
    "Omnichannel": 0.2,
    "Retail Members": 0.25,
    "Retail Walk-In": 0.55,
}


PAYMENT_CONFIG: dict[str, PaymentMethodConfig] = {
    "Online": {
        "methods": ["Credit Card", "Debit Card", "Digital Wallet", "Buy Now Pay Later"],
        "weights": [0.35, 0.2, 0.35, 0.1],
    },
    "In Store": {
        "methods": ["Credit Card", "Cash", "Debit Card"],
        "weights": [0.55, 0.2, 0.25],
    },
}


DISCOUNT_PROB_BY_SEGMENT = {
    "New Customers": (0.7, 0.8),
    "Active Customers": (0.65, 0.75),
    "Churn Risk Customers": (0.8, 0.9),
    "High Spenders": (0.55, 0.65),
    "Budget Shoppers": (0.85, 0.95),
}
