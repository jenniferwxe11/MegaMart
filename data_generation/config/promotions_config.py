DOLLAR_DISCOUNT_MAX_RATIO = 0.40
PERCENTAGE_DISCOUNT_MAX_PCT = 40.0

PROMOTION_THEMES = {
    "Seasonal": ["Seasonal Savings", "Limited-Time Deals", "Festive Specials"],
    "Acquisition": ["Welcome Deals", "New Shopper Specials"],
    "Retention": ["Member Exclusives", "Loyalty Rewards"],
    "Clearance": ["Final Markdowns", "Clearance Sale"],
}


PROMO_NAME_TEMPLATES = {
    "Category": [
        "{category} Savings",
        "Deals on {category}",
        "{category} Weekly Specials",
        "Stock Up on {category}",
    ],
    "Free Shipping": [
        "Free Delivery on Us",
        "Free Shipping Special",
        "Online Order Bonus",
    ],
    "Bundle": ["Bundle & Save", "Value Pack Deals", "Special Bundle Offer"],
}


PROMOTION_TYPE_PROB = {
    "percentage_discount": 0.5,
    "dollar_discount": 0.25,
    "free_shipping": 0.15,
    "bundle": 0.1,
}


MECHANIC_SCOPE_RULES = {
    "free_shipping": ["cart"],
    "percentage_discount": ["category", "product"],
    "dollar_discount": ["category", "product"],
    "bundle": ["bundle"],
}


CHANNEL_PROMOTION_COMPATIBILITY = {
    "Email": ["free_shipping", "percentage_discount"],
    "Push Notifications": ["free_shipping", "percentage_discount"],
    "Paid Advertisements": ["percentage_discount", "bundle"],
    "In-App": ["bundle", "percentage_discount"],
    "SMS": ["free_shipping"],
}


CAMPAIGN_PROMOTION_STRATEGY = {
    "Seasonal": {
        "primary": ["percentage_discount", "bundle"],
        "secondary": ["free_shipping"],
        "promo_count": (2, 3),
    },
    "Clearance": {
        "primary": ["dollar_discount"],
        "secondary": ["percentage_discount"],
        "max_promotions": (1, 2),
    },
    "Acquisition": {
        "primary": ["free_shipping", "percentage_discount"],
        "secondary": [],
        "max_promotions": (1, 2),
    },
    "Retention": {
        "primary": ["percentage_discount"],
        "secondary": ["free_shipping"],
        "max_promotions": (1, 2),
    },
}


OFFER_TO_PROMOTION_COMPATIBILITY = {
    "First Order Deal": {
        "promotion_scope": "customer",
        "promotion_mechanic": [
            "percentage_discount",
            "dollar_discount",
            "free_shipping",
        ],
    },
    "Free Shipping": {
        "promotion_scope": "cart",
        "promotion_mechanic": ["free_shipping"],
    },
    "Discount on Cart": {
        "promotion_scope": "cart",
        "promotion_mechanic": ["percentage_discount", "dollar_discount"],
    },
    "Discount on Category": {
        "promotion_scope": "category",
        "promotion_mechanic": ["percentage_discount", "dollar_discount"],
    },
    "Bundles": {
        "promotion_scope": "bundle",
        "promotion_mechanic": ["bundle"],
    },
}


STACKING_PRIORITY = {
    "bundle": 4,
    "product": 3,
    "category": 2,
    "cart": 1,
}


CATEGORY_PROMOTION_PROB = {
    # High-frequency promo categories (impulse / competitive)
    "Snacks": 0.35,
    "Beverages": 0.30,
    "Bakery": 0.28,
    "Frozen Food": 0.25,
    "Breakfast Foods": 0.25,
    # Medium-frequency promo categories
    "Dairy & Eggs": 0.22,
    "Fresh Produce": 0.20,
    "Personal Care": 0.20,
    "Canned Goods": 0.18,
    "Pantry Staples": 0.18,
    # Lower-frequency (planned purchase / margin-sensitive)
    "Cleaning Supplies": 0.15,
    "Household Essentials": 0.14,
    "Baby Products": 0.12,
    "Health & Beauty": 0.12,
    # Rarely promoted
    "Meat & Seafood": 0.10,
    "Rice & Noodles": 0.10,
    # Very rare / event-based
    "Electronics & Appliances": 0.05,
    "Home & Living": 0.06,
    "Sports, Travel & Leisure": 0.06,
}


CATEGORY_PERCENT_DISCOUNT_RANGE = {
    "Snacks": (5, 20),
    "Beverages": (5, 20),
    "Bakery": (10, 25),
    "Frozen Food": (10, 25),
    "Electronics & Appliances": (10, 40),
    "Home & Living": (10, 35),
}


CATEGORY_DOLLAR_DISCOUNT_CAP = {
    "Snacks": 5,
    "Beverages": 5,
    "Bakery": 8,
    "Frozen Food": 10,
    "Electronics & Appliances": 200,
    "Home & Living": 100,
}


MIN_SPEND_FOR_FREE_SHIPPING = {
    "Seasonal": 80,  # higher AOV expectations
    "Clearance": 60,
    "Acquisition": 50,
    "Retention": 40,  # reward loyalty
}


MIN_SPEND_PER_CATEGORY = {
    "Snacks": 20,
    "Beverages": 20,
    "Dairy & Eggs": 25,
    "Frozen Food": 30,
    "Fresh Produce": 25,
    "Pantry Staples": 30,
    "Household Essentials": 35,
    "Health & Beauty": 40,
    "Baby Products": 40,
    "Canned Goods": 25,
    "Personal Care": 35,
    "Meat & Seafood": 45,
    "Bakery": 20,
    "Cleaning Supplies": 35,
    "Rice & Noodles": 30,
    "Breakfast Foods": 25,
    "Electronics & Appliances": 150,
    "Home & Living": 80,
    "Sports, Travel & Leisure": 100,
}


BUNDLE_CAMPAIGN_COMPATIBILITY = {
    # no price maths
    "Seasonal": [
        "Set",
        "2 For X",
    ],
    # deplet stock fast
    "Clearance": [
        "Buy One, Get One",
        "Buy N Save X",
    ],
    # builds habit & basket size
    "Retention": [
        "Set",
        "Buy N Save X",
        "2 For X",
    ],
    # low risk purchase
    "Acquisition": [
        "Buy One, Get One",
        "2 For X",
        "Set",
    ],
}


# PRIMARY_OFFER_PROB = {
#     "Acquisition": {
#         "First Order Deal": 0.65,
#         "Free Shipping": 0.25,
#         "Discount on Cart": 0.10,
#     },
#     "Retention": {
#         "Discount on Cart": 0.60,
#         "Discount on Category": 0.25,
#         "Free Shipping": 0.15,
#     },
#     "Clearance": {
#         "Bundles": 0.55,
#         "Discount on Category": 0.30,
#         "Discount on Cart": 0.15,
#     },
#     "Seasonal": {
#         "Discount on Category": 0.45,
#         "Discount on Cart": 0.30,
#         "Bundles": 0.25,
#     },
# }


# MULTI_OFFER_PROB = {
#     "Acquisition": 0.05,
#     "Retention": 0.10,
#     "Clearance": 0.35,
#     "Seasonal": 0.25,
# }


# SECONDARY_OFFER_COMPATIBILITY = {
#     "Free Shipping": [],
#     "Discount on Category": ["Free Shipping"],
#     "Discount on Cart": ["Free Shipping"],
#     "Bundles": ["Free Shipping"],
#     "First Order Deal": ["Free Shipping"],
# }


# CATEGORY_CAMPAIGN_PROBABILITY = {
#     "Snacks": 0.15,
#     "Beverages": 0.12,
#     "Dairy & Eggs": 0.05,
#     "Frozen Food": 0.04,
#     "Fresh Produce": 0.02,
#     "Pantry Staples": 0.01,
#     "Household Essentials": 0.01,
#     "Health & Beauty": 0.05,
#     "Baby Products": 0.03,
#     "Canned Goods": 0.02,
#     "Personal Care": 0.05,
#     "Meat & Seafood": 0.03,
#     "Bakery": 0.04,
#     "Cleaning Supplies": 0.01,
#     "Rice & Noodles": 0.01,
#     "Breakfast Foods": 0.03,
#     "Electronics & Appliances": 0.10,
#     "Home & Living": 0.05,
#     "Sports, Travel & Leisure": 0.08,
# }
