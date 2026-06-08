SEASONAL_PEAK_MONTHS = {
    1: 0.5,
    2: 0.6,
    3: 0.7,
    4: 0.8,
    5: 0.9,
    6: 1.0,
    7: 1.1,
    8: 1.2,
    9: 1.3,
    10: 1.4,
    11: 1.8,  # 11.11
    12: 2.0,  # 12.12 + Christmas
}


TARGET_SEGMENT = {
    "New Customers": 0.2,
    "Active Customers": 0.5,
    "Churn Risk Customers": 0.1,
    "High Spenders": 0.1,
    "Budget Shoppers": 0.1,
}


DEVICE_CATEGORY = {
    "Mobile": 0.72,
    "Desktop": 0.23,
    "Tablet": 0.05,
}


DEVICE_PLATFORM = {
    "Mobile": {
        "iOS": 0.45,
        "Android": 0.55,
    },
    "Tablet": {
        "iOS": 0.35,
        "Android": 0.65,
    },
    "Desktop": {
        "Web": 1.0,
    },
}


SEGMENT_CATEGORY_BIAS = {
    "New Customers": {
        "Snacks": 1.4,
        "Beverages": 1.3,
    },
    "High Spenders": {
        "Electronics & Appliances": 1.8,
        "Home & Living": 1.5,
        "Sports, Travel & Leisure": 1.4,
    },
    "Budget Shoppers": {
        "Canned Goods": 1.5,
        "Dairy & Eggs": 1.4,
        "Frozen Food": 1.3,
        "Household Essentials": 1.4,
        "Pantry Staples": 1.3,
        "Rice & Noodles": 1.3,
    },
}
