NATURAL_PRODUCT_NAME_VARIATION_RATE = 0.08
NATURAL_BRAND_VARIATION_RATE = 0.05
NATURAL_CATEGORY_VARIATION_RATE = 0.08
NATURAL_SELLING_PRICE_VARIATION_RATE = 0.10


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


CATEGORY_TO_STORE = {
    "Snacks": [
        "Chips & Chocolate",
        "Sweet & Salty Treats",
        "Tidbits",
        "Chips",
        "Snack Food",
    ],
    "Beverages": ["Soft Drinks", "Drinks"],
    "Dairy & Eggs": [
        "Dairy",
        "Dairy, Chilled & Eggs",
        "Chilled",
        "Milk & Eggs",
        "Fresh Dairy",
    ],
    "Frozen Food": ["Frozen"],
    "Fresh Produce": ["Vegetables & Fruits", "Fruits & Vegetables"],
    "Pantry Staples": [
        "Cupboard Essentials",
        "Rice, Noodles & Cooking Ingredients",
        "Cooking Ingredients",
        "Staples",
        "Daily Essentials",
    ],
    "Household Essentials": [
        "Household",
        "Cleaning",
        "Household Items",
        "Essentials",
    ],
    "Health & Beauty": ["Beauty", "Beauty & Personal Care", "Personal Care"],
    "Baby Products": ["Mummy & Baby", "Baby", "Baby & Child"],
    "Canned Goods": ["Canned Food", "Food Cupboard"],
    "Personal Care": ["Personal Care & Hygiene", "Health & Beauty"],
    "Meat & Seafood": ["Meat and Seafood"],
    "Bakery": ["Bread"],
    "Cleaning Supplies": [
        "Cleaning",
        "Household Cleaning",
    ],
    "Rice & Noodles": [
        "Rice & Pasta",
        "Food Cupboard",
        "Rice, Noodles & Cooking Ingredients",
    ],
    "Breakfast Foods": ["Granolas & Cereals", "Food Cupboard", "Breakfast"],
    "Electronics & Appliances": ["Electronics"],
    "Home & Living": ["Home & Living (Kitchenware, Storage, Bedding)", "Home Living"],
    "Sports, Travel & Leisure": [
        "Lifestyle & Recreation (Fitness, Toys, Travel)",
        "Sports & Travel",
        "Lifestyle",
    ],
}
