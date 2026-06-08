# Minimum days each phase must occupy to be worth splitting into
MIN_PHASE_DAYS = 14
# Minimum total window length before we attempt multi-phase pricing
MIN_WINDOW_FOR_SPLIT = MIN_PHASE_DAYS * 2


# PROMO / EOL are modest step-downs — not a fresh large discount.
MAX_DISCOUNT_PCT = {
    "LAUNCH": 0.25,
    "PROMO": 0.30,
    "EOL": 0.33,
}


# How many extra percentage points each subsequent phase may add
PHASE_STEP = {"PROMO": 0.05, "EOL": 0.03}


BUNDLE_DEFINITIONS = {
    "Buy One, Get One": {
        # perishable
        "Buy 1 Get 1 Free Fresh Produce Pack": ["Fresh Produce"],
        "Buy 1 Get 1 Free Bakery Foods": ["Bakery"],
    },
    "Set": {
        # encourage cross category purchase
        "Breakfast Combo": ["Breakfast Foods", "Dairy & Eggs"],
        "Self Care Set": ["Health & Beauty", "Personal Care"],
        "Movie Night Set": ["Snacks", "Beverages"],
        "Guilty Pleasure Duo": ["Snacks", "Frozen Food"],
        "Household Essentials Pack": ["Household Essentials", "Cleaning Supplies"],
        "Baby Care Starter Set": ["Baby Products", "Household Essentials"],
    },
    "2 For X": {
        # impulse buy
        "2 for $X Snack Pack": ["Snacks"],
        "2 for $X Drink Pack": ["Beverages"],
        "2 for $X Frozen Pack": ["Frozen Food"],
    },
    "Buy N Save X": {
        # basket expansion
        "Buy 3 Save $X Pantry Staples Pack": ["Pantry Staples"],
        "Buy 4 Save $X Personal Care Pack": ["Personal Care"],
        "Buy 3 Save $X Rice & Noodles Pack": ["Rice & Noodles"],
        "Buy 3 Save $X Canned Goods Pack": ["Canned Goods"],
        "Buy 3 Save $X Dairy Pack": ["Dairy & Eggs"],
        "Buy 3 Save $X Meat & Seafood Pack": ["Meat & Seafood"],
    },
}
