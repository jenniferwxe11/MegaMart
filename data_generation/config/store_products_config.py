BRAND_ERROR_RATE = 0.05
CATEGORY_ERROR_RATE = 0.08
NAME_ERROR_RATE = 0.15
PRICE_ERROR_RATE = 0.1
NATURAL_NAME_VARIATION_RATE = 0.08  # down from ~0.25 across sub-functions
NATURAL_BRAND_VARIATION_RATE = 0.05  # down from ~0.20


STORE_TYPE_CONFIG = {
    "Neighbourhood": {
        "Assortment": (0.25, 0.4),
        "Essential": (0.4, 0.6),
    },
    "Mall": {
        "Assortment": (0.6, 0.8),
        "Essential": (0.25, 0.35),
    },
    "Online": {
        "Assortment": (0.95, 1),
        "Essential": (0.2, 0.3),
    },
    "Flagship": {
        "Assortment": (0.97, 1),
        "Essential": (0.4, 0.5),
    },
}


ESSENTIAL_CATEGORIES = [
    "Snacks",
    "Beverages",
    "Dairy & Eggs",
    "Fresh Produce",
    "Pantry Staples",
    "Household Essentials",
    "Rice & Noodles",
    "Cleaning Suppliers",
    "Personal Care",
]


DESCRIPTOR_MAP = {
    "Original": ["Classic", "Regular"],
    "Organic": ["Natural", "Pure"],
    "Family Pack": ["Value Pack", "Large Pack"],
    "Heavy Duty": ["Strong", "Powerful"],
    "Portable": ["Lightweight"],
    "Compact": ["Mini", "Small"],
    "Eco-Friendly": ["Green", "Sustainable"],
    "Gluten-Free": ["Wheat-Free", "Celiac-Friendly"],
    "Low Sugar": ["Reduced Sugar", "Sugar-Free"],
}
