from datetime import date, datetime
from typing import Any, Dict, List

# sample mode
DATA_START_DATE = date(2023, 1, 1)
DATA_END_DATE = date(2025, 12, 31)
SIMULATION_DATE = date(2025, 12, 31)
NUM_CUSTOMERS = 100
NUM_PHYSICAL_STORES = 5
NUM_PRODUCTS = 50
BRAND_ERROR_RATE = 1
CATEGORY_ERROR_RATE = 1
NAME_ERROR_RATE = 1
PRICE_ERROR_RATE = 1
NUM_REVIEWS = 100
NUM_CAMPAIGNS = 200
CONTROL_GROUP_PERCENTAGE = 0.5
AUDIENCE_PERCENTAGE = 1
NUM_CLICKSTREAMS = 100
PAYDAY_BOOST = 2.5
PARETO_ALPHA = 1.8
MAX_SESSIONS = 5
MAX_EVENTS_PER_SESSION = 20
MAX_CLICKSTREAM = 200
NUM_TRANSACTIONS = 10
# production mode
# MAX_SESSIONS = 50
# MAX_EVENTS_PER_SESSION = 60
# BRAND_ERROR_RATE = 0.05
# CATEGORY_ERROR_RATE = 0.08
# NAME_ERROR_RATE = 0.15
# PRICE_ERROR_RATE = 0.1


MONTH_WEIGHTS_2024 = {
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


MALL_TO_AREA = {
    "Waterway Point": "Punggol",
    "Junction 8": "Bishan",
    "IMM": "Jurong East",
    "Northpoint": "Yishun",
    "Hougang Mall": "Hougang",
    "Causeway Point": "Woodlands",
    "NEX": "Serangoon",
    "VivoCity": "HarbourFront",
    "ION": "Orchard",
    "313@Somerset": "Somerset",
    "Bugis+": "Bugis",
    "The Seletar Mall": "Seletar",
    "Ang Mo Kio Hub": "Ang Mo Kio",
    "Sun Plaza": "Sembawang",
    "City Square Mall": "Farrer Park",
    "Westgate": "Jurong East",
    "JEM": "Jurong East",
    "Lot One": "Choa Chu Kang",
    "White Sands": "Pasir Ris",
    "Clarke Quay Central": "Clarke Quay",
    "Eastpoint Mall": "Pasir Ris",
    "Marina Square": "Marina Bay",
    "Raffles City": "Downtown Core",
    "Tampines Mall": "Tampines",
    "Great World City": "River Valley",
    "Plaza Singapura": "Dhoby Ghaut",
    "Orchard Central": "Orchard",
    "The Centrepoint": "Orchard",
    "Suntec City": "Marina Centre",
    "Funan Mall": "City Hall",
    "The Star Vista": "Buona Vista",
    "Bedok Mall": "Bedok",
    "Changi City Point": "Changi",
    "The Cathay": "Dhoby Ghaut",
    "Velocity": "Novena",
    "Kallang Wave Mall": "Kallang",
    "The Rail Mall": "Upper Bukit Timah",
    "The Clementi Mall": "Clementi",
    "Tanglin Mall": "Tanglin",
    "Millenia Walk": "Marina Bay",
    "West Coast Plaza": "West Coast",
    "Bukit Panjang Plaza": "Bukit Panjang",
    "Tiong Bahru Plaza": "Tiong Bahru",
    "Anchorpoint": "Alexandra",
    "The Woodleigh Mall": "Woodleigh",
    "Citylink Mall": "City Hall",
    "UE Square": "Bugis",
    "i12 Katong": "Marine Parade",
    "Marine Parade Central": "Marine Parade",
    "The Grandstand": "Bukit Timah",
    "Hillion Mall": "Bukit Panjang",
}


CATEGORIES = [
    "Snacks",
    "Beverages",
    "Dairy & Eggs",
    "Frozen Food",
    "Fresh Produce",
    "Pantry Staples",
    "Household Essentials",
    "Health & Beauty",
    "Baby Products",
    "Canned Goods",
    "Personal Care",
    "Meat & Seafood",
    "Bakery",
    "Cleaning Supplies",
    "Rice & Noodles",
    "Breakfast Foods",
    "Electronics & Appliances",
    "Home & Living",
    "Sports, Travel & Leisure",
]


SUBCATEGORIES = {
    "Home & Living": [
        "Kitchenware",
        "Storage & Organization",
        "Bedding & Furnishings",
    ],
    "Sports, Travel & Leisure": [
        "Fitness & Wellness",
        "Travel Gear",
        "Games & Hobbies",
        "Outdoor Equipment",
    ],
}


BRANDS = {
    "Snacks": ["Lays", "Pringles", "Oreo", "Jack n Jill", "Ritz", "Nature Valley"],
    "Beverages": ["Coca-Cola", "Pepsi", "Heaven & Earth", "Nestle", "Pokka"],
    "Dairy & Eggs": ["Farmers Union", "Marigold", "Meiji", "SCS", "Cowhead", "Chew's"],
    "Frozen Food": ["CP", "McCain", "Farmpride", "First Pride"],
    "Fresh Produce": ["Dole", "Zespri", "Zenxin Organic Food", "Pasar", "Little Farms"],
    "Pantry Staples": [
        "Knife",
        "Lee Kum Kee",
        "Ayam Brand",
        "San Remo",
        "Golden Farm",
        "Maggie",
        "A1",
    ],
    "Household Essentials": ["Kleenex", "FairPrice", "Hada", "Premier"],
    "Health & Beauty": ["Colgate", "Dove", "Nivea", "L'Oreal", "Sensodyne"],
    "Baby Products": ["Pampers", "Huggies", "MamyPoko", "Johnson's"],
    "Canned Goods": ["Ayam Brand", "Campbell's", "Del Monte", "Heinz"],
    "Personal Care": [
        "Gillette",
        "Schick",
        "Lifebuoy",
        "Dettol",
        "Pantene",
        "Head & Shoulders",
    ],
    "Meat & Seafood": [
        "Ben's Farm",
        "Sadia",
        "Ocean Fresh",
        "Farmhouse",
        "Pasar Fresh",
        "Hego",
        "Kee Song",
        "Aw's Market",
    ],
    "Bakery": ["Gardenia", "Sunshine", "Mission", "Apollo"],
    "Cleaning Supplies": ["Mr Muscle", "Vanish", "Ajax", "Clorox"],
    "Rice & Noodles": ["Royal Umbrella", "SongHe", "Maggi", "Koka"],
    "Breakfast Foods": ["Kellogg's", "Quaker", "Post", "Nestlé"],
    "Electronics & Appliances": [
        "Philips",
        "Xiaomi",
        "Samsung",
        "Panasonic",
        "Dyson",
        "Toyomi",
    ],
    "Kitchenware": ["Lock&Lock", "Tefal", "Zojirushi"],
    "Storage & Organization": ["Lock&Lock", "HomeBasics"],
    "Bedding & Furnishings": ["Tempur", "HomeBasics"],
    "Fitness & Wellness": ["Nike", "Adidas", "Puma", "Fitbit", "Wilson"],
    "Travel Gear": ["American Tourister", "Nike", "Adidas"],
    "Games & Hobbies": ["Hasbro", "Mattel"],
    "Outdoor Equipment": ["Coleman", "Naturehike"],
}


CATEGORY_ITEMS = {
    "Snacks": ["Chips", "Biscuits", "Bars", "Cookies", "Nuts", "Crackers"],
    "Beverages": ["Cola", "Juice", "Tea", "Coffee", "Soda", "Energy Drinks"],
    "Dairy & Eggs": ["Milk", "Cheese", "Butter", "Yogurt", "Cream", "Eggs"],
    "Frozen Food": ["Pizza", "Fries", "Dumplings", "Ice Cream", "Frozen Vegetables"],
    "Fresh Produce": [
        "Apples",
        "Bananas",
        "Carrots",
        "Tomatoes",
        "Spinach",
        "Broccoli",
        "Potatoes",
        "Lettuce",
        "Cucumbers",
        "Peppers",
    ],
    "Pantry Staples": [
        "Cooking Oil",
        "Salt",
        "Sugar",
        "Flour",
        "Tumeric",
        "Mustard",
        "Vinegar",
        "Honey",
        "Soy Sauce",
        "Ketchup",
        "Chili Sauce",
        "Mayonnaise",
    ],
    "Household Essentials": [
        "Toilet Paper",
        "Trash Bags",
        "Detergent Pods",
        "Soap Refills",
        "Paper Towels",
        "Facial Tissues",
        "Fabric Softener",
        "Air Freshener",
    ],
    "Health & Beauty": ["Toothpaste", "Lotion", "Shampoo", "Conditioner", "Body Wash"],
    "Baby Products": ["Diapers", "Wipes", "Powder", "Cream", "Formula"],
    "Canned Goods": [
        "Tomatoes",
        "Corn",
        "Beans",
        "Tuna",
        "Sardines",
        "Mushroom",
        "Pickles",
    ],
    "Personal Care": ["Deodorant", "Shaving Foam", "Razors", "Hand Sanitizer"],
    "Meat & Seafood": [
        "Chicken",
        "Beef",
        "Fish",
        "Prawns",
        "Salmon",
        "Lamb",
        "Turkey",
        "Fillet",
        "Drumsticks",
    ],
    "Bakery": ["Bread", "Cake", "Buns", "Croissant", "Muffin"],
    "Cleaning Supplies": [
        "Bleach",
        "All-purpose Spray",
        "Scrub Brush",
        "Wipes",
        "Dish Soap",
        "Floor Cleaner",
        "Glass Cleaner",
        "Sponges",
    ],
    "Rice & Noodles": [
        "Rice",
        "Soba",
        "Udon",
        "Noodles",
        "Vermicelli",
        "Spaghetti",
        "Macaroni",
        "Fettuccine",
        "Lasagna",
        "Penne",
        "Ramen",
    ],
    "Breakfast Foods": ["Cereal", "Oats", "Granola", "Muesli", "Porridge"],
    "Electronics & Appliances": [
        "Blender",
        "Air Fryer",
        "Vacuum Cleaner",
        "Microwave",
        "Refrigerator",
        "Washing Machine",
        "Toaster",
        "Coffee Maker",
        "Hair Dryer",
        "Electric Kettle",
        "Rice Cooker",
        "Fan",
    ],
}


SUBCATEGORY_ITEMS = {
    "Kitchenware": [
        "Cookware",
        "Food Containers",
        "Water Bottles",
        "Cutleries",
    ],
    "Storage & Organization": [
        "Storage Boxes",
        "Wardrobe Organizers",
        "Shelving Units",
    ],
    "Bedding & Furnishings": [
        "Bedsheets",
        "Pillows",
        "Curtains",
        "Rugs",
    ],
    "Fitness & Wellness": [
        "Dumbbells",
        "Yoga Mat",
        "Resistance Bands",
        "Fitness Tracker",
    ],
    "Travel Gear": [
        "Suitcase",
        "Backpack",
        "Travel Pillow",
    ],
    "Games & Hobbies": [
        "Board Games",
        "Puzzle Sets",
    ],
    "Outdoor Equipment": [
        "Camping Tent",
        "Sleeping Bag",
    ],
}


CATEGORY_PROFILES: Dict[str, Dict[str, List[Any]]] = {
    "Snacks": {
        "variants": [None, "Original", "Baked", "Chocolate", "Honey", "Salted"],
        "net_content": ["50g", "100g", "150g", "300g"],
        "pack_quantity": [None],
    },
    "Beverages": {
        "variants": [None, "Original", "Zero Sugar", "Less Sugar", "Concentrate"],
        "net_content": ["330ml", "500ml", "1L", "1.5L"],
        "pack_quantity": [None, "6-pack", "12-pack", "24-pack"],
    },
    "Dairy & Eggs": {
        "variants": [None, "Value", "Imported", "Local", "Organic", "Pasteurised"],
        "net_content": [None],
        "pack_quantity": [None, "2-pack", "4-pack"],
    },
    "Frozen Food": {
        "variants": [None, "Family Pack", "Single Serve", "Low Calorie"],
        "net_content": ["400g", "800g", "1kg"],
        "pack_quantity": [None, "2-pack"],
    },
    "Fresh Produce": {
        "variants": [
            None,
            "Organic",
            "Local",
            "Imported",
            "Washed",
            "Pre-cut",
            "Whole",
        ],
        "net_content": ["Loose", "250g", "500g"],
        "pack_quantity": [None],
    },
    "Pantry Staples": {
        "variants": [None, "Organic", "Shelf Stable"],
        "net_content": [None],
        "pack_quantity": [None],
    },
    "Household Essentials": {
        "variants": [None, "Regular", "Eco", "Bulk", "Travel Size"],
        "net_content": [None],
        "pack_quantity": [None, "2-pack", "4-pack"],
    },
    "Health & Beauty": {
        "variants": [None, "Sensitive", "Whitening", "Herbal", "Cooling"],
        "net_content": ["100ml", "200ml", "400ml"],
        "pack_quantity": [None, "2-pack"],
    },
    "Baby Products": {
        "variants": [None, "Newborn", "Toddler", "Premium"],
        "net_content": [None],
        "pack_quantity": [None],
    },
    "Canned Goods": {
        "variants": [None, "Reduced Salt"],
        "net_content": ["200g", "400g", "800g"],
        "pack_quantity": [None],
    },
    "Personal Care": {
        "variants": [None, "Travel Size"],
        "net_content": ["50ml", "100ml", "200ml"],
        "pack_quantity": [None, "2-pack"],
    },
    "Meat & Seafood": {
        "variants": [
            None,
            "Fresh",
            "Frozen",
            "Marinated",
            "Smoked",
            "Boneless",
            "Skinless",
            "Organic",
        ],
        "net_content": ["300g", "500g", "800g", "1kg"],
        "pack_quantity": [None],
    },
    "Bakery": {
        "variants": [
            None,
            "Wholemeal",
            "Multigrain",
            "Sourdough",
            "Butter",
            "Chocolate",
            "Almond",
            "Cheese",
            "Gluten-Free",
        ],
        "net_content": [None],
        "pack_quantity": [None, "2-pack", "6-pack"],
    },
    "Cleaning Supplies": {
        "variants": [None, "Eco-Friendly", "Heavy Duty", "Antibacterial"],
        "net_content": ["500ml", "1L", "2L"],
        "pack_quantity": [None, "2-pack", "4-pack"],
    },
    "Rice & Noodles": {
        "variants": [None, "Wholegrain", "Organic", "Gluten-Free", "Instant"],
        "net_content": [None, "100g", "250g", "500g"],
        "pack_quantity": [None, "2-pack", "5-pack"],
    },
    "Breakfast Foods": {
        "variants": [
            None,
            "Honey",
            "Low Sugar",
            "Fuits",
            "Multigrain",
            "Protein",
            "Gluten-Free",
            "High Fiber",
            "Kids",
        ],
        "net_content": ["100g", "250g", "500g"],
        "pack_quantity": [
            None,
            "2-pack",
            "4-pack",
        ],
    },
    "Electronics & Appliances": {
        "variants": [None, "Mini", "Low Power", "Smart", "Energy Saving", "Quiet"],
        "net_content": [None],
        "pack_quantity": [None],
        "colour": [None, "White", "Grey", "Black"],
    },
    "Home & Living": {
        "variants": [None, "Durable", "Eco-Friendly"],
        "net_content": [None],
        "pack_quantity": [None],
    },
    "Sports, Travel & Leisure": {
        "variants": [None, "Portable", "Compact", "Adjustable"],
        "net_content": [None],
        "pack_quantity": [None],
    },
}


# Approximate price ranges per category
CATEGORY_PRICE_RANGES = {
    # per 100g/100ml
    "Snacks": (0.3, 1.5),
    "Beverages": (0.15, 1.2),
    "Frozen Food": (0.6, 2.5),
    "Fresh Produce": (0.8, 2.2),
    "Health & Beauty": (1.0, 6.0),
    "Canned Goods": (0.25, 1.5),
    "Personal Care": (1.0, 6.0),
    "Meat & Seafood": (1.2, 6.0),
    "Cleaning Supplies": (0.8, 4.0),
    "Breakfast Foods": (0.4, 2.5),
    "Rice & Noodles": (0.6, 1.5),
    # per pack
    "Dairy & Eggs": (2.0, 6.0),
    "Bakery": (1.2, 3.5),
    "Household Essentials": (1.2, 5.0),
    # item count
    "Pantry Staples": (1.5, 8.0),
    "Baby Products": (8.0, 40.0),
    "Home & Living": (10.0, 120.0),
    "Sports, Travel & Leisure": (15.0, 200.0),
    "Electronics & Appliances": (20.0, 500.0),
}


# Cost price as % of selling price:
CATEGORY_COST_MARGIN = {
    "Snacks": (0.4, 0.7),
    "Beverages": (0.4, 0.7),
    "Dairy & Eggs": (0.5, 0.8),
    "Frozen Food": (0.5, 0.8),
    "Fresh Produce": (0.3, 0.6),
    "Pantry Staples": (0.5, 0.8),
    "Household Essentials": (0.5, 0.8),
    "Health & Beauty": (0.5, 0.85),
    "Baby Products": (0.5, 0.85),
    "Canned Goods": (0.4, 0.75),
    "Personal Care": (0.5, 0.85),
    "Meat & Seafood": (0.5, 0.75),
    "Bakery": (0.4, 0.7),
    "Cleaning Supplies": (0.5, 0.8),
    "Rice & Noodles": (0.5, 0.8),
    "Breakfast Foods": (0.5, 0.8),
    "Electronics & Appliances": (0.7, 0.95),
    "Home & Living": (0.6, 0.9),
    "Sports, Travel & Leisure": (0.6, 0.9),
}


PRODUCT_LIFECYCLE = {
    # "New": 0.1,
    "Active": 0.7,
    "Seasonal": 0.1,
    "Discontinued": 0.1,
}


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


CATEGORY_TO_STORE = {
    "Snacks": ["Chips & Chocolate", "Sweet & Salty Treats", "Snacks & Confectionery"],
    "Beverages": ["Soft Drinks", "Drinks"],
    "Dairy & Eggs": ["Dairy", "Dairy, Chilled & Eggs"],
    "Frozen Food": ["Frozen"],
    "Fresh Produce": ["Vegetables & Fruits", "Fruits & Vegetables"],
    "Pantry Staples": [
        "Cupboard Essentials",
        "Rice, Noodles & Cooking Ingredients",
        "Cooking Ingredients",
    ],
    "Household Essentials": ["Household"],
    "Health & Beauty": ["Beauty", "Beauty & Personal Care", "Personal Care"],
    "Baby Products": ["Mummy & Baby", "Baby", "Baby & Child"],
    "Canned Goods": ["Canned Food", "Food Cupboard"],
    "Personal Care": ["Personal Care & Hygiene", "Health & Beauty"],
    "Meat & Seafood": [""],
    "Bakery": ["Bread"],
    "Cleaning Supplies": ["Soft Drinks"],
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

CATEGORY_ATTRIBUTES = {
    "Snacks": [
        "dietary_tag(vegan, gluten-free)",
        "allergen_info",
        "is_sweet/savoury",
        "is_baked/fried",
        "texture(crispy, chewy)",
    ],
    "Beverages": [
        "beverage_type(soda, juice, tea)",
        "caffine_content",
        "carbonation(yes/no)",
        "is_concentrate",
        "serving_temperature",
        "packaging_type(can/bottle)",
    ],
    "Dairy & Eggs": [
        "lactose_free",
        "storage_type(chilled/room temperature)",
        "expiry_date",
        "source(cow, free-range)",
        "pasteurised(yes/no)",
    ],
    "Frozen Food": [
        "is_pre_cooked",
        "cooking_method(oven, air fryer, stove)",
        "cook_time_minutes",
    ],
    "Fresh Produce": [
        "country_of_origin",
        "wash_type(washed/unwashed)",
        "cut_type(whole, pre-cut)",
        "seasonality",
        "perishability_score",
        "organic_certified",
    ],
    "Pantry Staples": ["shelf_life_days", "allergen_info", "country_of_origin"],
    "Household Essentials": [
        "disposable/reusable",
        "scent",
        "refillable",
        "eco-certified",
    ],
    "Health & Beauty": [
        "skin_type",
        "dermatologically_tested",
        "gender_target",
        "fragrance_free",
    ],
    "Baby Products": [
        "hypoallergenic",
        "safety_certification",
        "baby_stage(newborn, toddler)",
        "fragrance_free",
    ],
    "Canned Goods": [
        "pull_tab(yes/no)",
        "ready_to_eat",
        "liquid_base(oil, brine, syrup)",
    ],
    "Personal Care": ["alcohol_free", "dermatologist_tested", "skin_type"],
    "Meat & Seafood": [
        "cut_type",
        "country_of_origin",
        "farmed_or_wild",
        "storage_temperature",
        "expiry_days",
        "halal_certified",
    ],
    "Bakery": ["baked_today(yes/no)", "contains_nuts", "shelf_life_days"],
    "Cleaning Supplies": ["eco_certified", "antibacterial", "dilution_required"],
    "Rice & Noodles": [
        "instant(yes/no)",
        "gluten_free",
        "country_of_origin",
        "cooking_time",
    ],
    "Breakfast Foods": ["fibre_content", "kids_focused"],
    "Electronics & Appliances": [
        "power_rating",
        "dimensions",
        "weight",
        "color",
        "warranty_period",
        "noise_level",
        "country_of_manufacture",
        "is_smart",
    ],
    "Home & Living": [
        "dimensions",
        "weight",
        "assembly_required",
        "color",
        "care_instructions",
        "eco_certified",
        "durability_rating",
    ],
    "Sports, Travel & Leisure": [
        "usage_area(indoor/outdoor)",
        "weight",
        "skill_level",
        "weather_resistant",
        "durability_rating",
        "portability",
    ],
}


QUALITY_UPDATE_POLICY = {
    "poor": None,
    "average": 2,
    "good": 1,
    "excellent": 0,
}


GLOBAL_DESCRIPTORS = {
    "packaging": {
        "positive": ["well-packaged", "securely packaged", "neatly packed"],
        "neutral": ["standard packaging", "average packaging"],
        "negative": ["loosely packaged", "damaged", "flimsy packaging"],
    },
    "promotion": {
        "positive": ["good deal", "limited offer", "buy 1 get 1"],
        "neutral": ["standard offer", "price as usual"],
        "negative": ["expensive for value", "poor deal", "not worth the promotion"],
    },
}


POSITIVE_CATEGORY_DESCRIPTORS = {
    "Snacks": {
        "taste": ["salty", "savory", "spicy", "sweet", "umami", "tangy"],
        "texture": ["crunchy", "crispy", "soft", "chewy", "firm", "flaky"],
    },
    "Beverages": {
        "taste": ["sweet", "bitter", "refreshing", "sour", "fruity", "carbonated"],
        "texture": ["smooth", "frothy", "watery", "creamy", "thick", "light"],
    },
    "Dairy & Eggs": {
        "taste": ["creamy", "milky", "rich", "bland", "fresh", "tangy"],
        "texture": ["soft", "smooth", "runny", "firm", "dense", "fluffy"],
    },
    "Frozen Food": {
        "taste": ["savory", "bland", "spicy", "rich"],
        "texture": ["soft", "crispy", "chewy", "frozen", "flaky"],
    },
    "Fresh Produce": {
        "taste": ["fresh", "sweet", "bitter", "tangy", "juicy", "earthy"],
        "texture": ["crisp", "firm", "soft", "juicy", "fibrous"],
    },
    "Pantry Staples": {
        "taste": ["fresh", "rich", "consistent", "high-quality"],
    },
    "Household Essentials": {
        "texture": ["smooth", "abrasive", "soft", "durable"],
        "packaging": ["easy to open", "leak-proof", "compact", "bulk"],
    },
    "Health & Beauty": {
        "texture": ["smooth", "silky", "creamy", "moisturizing", "light"],
        "scent": ["floral", "fresh", "fruity", "herbal", "unscented"],
    },
    "Baby Products": {
        "texture": ["soft", "gentle", "absorbent", "smooth"],
        "scent": ["mild", "unscented", "fresh", "soothing"],
    },
    "Canned Goods": {
        "taste": ["savory", "bland", "spicy", "sweet"],
        "texture": ["soft", "firm", "chunky", "smooth"],
    },
    "Personal Care": {
        "texture": ["smooth", "creamy", "gentle", "soft", "moisturizing"],
        "scent": ["floral", "fresh", "fruity", "unscented", "soothing"],
    },
    "Meat & Seafood": {
        "taste": ["savory", "umami", "rich", "fresh", "slightly sweet"],
        "texture": ["tender", "firm", "juicy", "flaky", "chewy"],
    },
    "Bakery": {
        "taste": ["buttery", "sweet", "savory", "flavorful", "rich", "fresh"],
        "texture": ["soft", "fluffy", "crispy", "crumbly", "chewy"],
    },
    "Cleaning Supplies": {
        "texture": ["smooth", "abrasive", "soft", "foamy"],
        "scent": ["fresh", "citrusy", "unscented", "clean"],
    },
    "Rice & Noodles": {
        "taste": ["bland", "savory", "nutty", "umami", "slightly sweet"],
        "texture": ["soft", "firm", "chewy", "al dente", "fluffy"],
    },
    "Breakfast Foods": {
        "taste": ["sweet", "savory", "nutty", "fruity", "rich"],
        "texture": ["crispy", "soft", "fluffy", "smooth", "chewy"],
    },
    "Electronics & Appliances": {
        "performance": ["fast", "efficient", "powerful", "responsive", "smooth"],
        "build": ["durable", "sturdy", "lightweight", "compact", "well-built"],
        "usage": ["easy to use", "user-friendly", "intuitive", "versatile"],
    },
    "Home & Living": {
        "performance": [
            "practical",
            "functional",
            "reliable",
            "efficient",
            "versatile",
        ],
        "build": ["simple", "modern", "space-efficient", "well-designed", "aesthetic"],
        "usage": ["comfortable", "supportive", "pleasant", "cozy", "well-balanced"],
    },
    "Sports, Travel & Leisure": {
        "performance": ["effective", "balanced", "reliable", "good experience"],
        "build": ["durable", "robust", "long-lasting", "well-built"],
        "usage": [
            "portable",
            "easy to carry",
            "lightweight",
            "travel-friendly",
            "compact",
        ],
    },
}


NEUTRAL_CATEGORY_DESCRIPTORS = {
    "Snacks": {
        "taste": ["moderate", "balanced", "ordinary", "mild", "typical"],
        "texture": ["soft", "slightly crunchy", "standard", "average", "acceptable"],
    },
    "Beverages": {
        "taste": ["average", "mild", "slightly sweet", "standard", "typical"],
        "texture": ["light", "smooth", "watery", "average", "ordinary"],
    },
    "Dairy & Eggs": {
        "taste": ["mild", "plain", "average", "acceptable", "typical"],
        "texture": ["soft", "standard", "slightly firm", "average", "acceptable"],
    },
    "Frozen Food": {
        "taste": ["bland", "typical", "standard", "moderate"],
        "texture": ["soft", "slightly crispy", "acceptable", "frozen-like", "ordinary"],
    },
    "Fresh Produce": {
        "taste": ["average", "fresh enough", "ordinary", "mild", "typical"],
        "texture": ["firm enough", "soft", "average", "acceptable", "slightly crisp"],
    },
    "Pantry Staples": {
        "taste": ["standard", "typical", "average-quality"],
    },
    "Household Essentials": {
        "texture": ["standard", "soft", "average", "durable enough"],
        "packaging": ["normal packaging", "typical", "average"],
    },
    "Health & Beauty": {
        "texture": ["average", "smooth enough", "light", "acceptable"],
        "scent": ["mild", "barely noticeable", "neutral", "ordinary"],
    },
    "Baby Products": {
        "texture": ["soft enough", "acceptable", "average", "standard"],
        "scent": ["neutral", "unscented", "mild", "ordinary"],
    },
    "Canned Goods": {
        "taste": ["average", "typical", "plain", "standard"],
        "texture": ["soft enough", "average", "acceptable", "standard"],
    },
    "Personal Care": {
        "texture": ["average", "standard", "soft", "acceptable"],
        "scent": ["neutral", "mild", "barely noticeable", "ordinary"],
    },
    "Meat & Seafood": {
        "taste": ["ordinary", "mild", "standard", "average"],
        "texture": ["acceptable", "average", "firm enough", "typical"],
    },
    "Bakery": {
        "taste": ["average", "standard", "mildly sweet", "typical"],
        "texture": ["soft", "standard", "slightly fluffy", "acceptable"],
    },
    "Cleaning Supplies": {
        "texture": ["average", "standard", "smooth enough", "acceptable"],
        "scent": ["mild", "neutral", "barely noticeable", "ordinary"],
    },
    "Rice & Noodles": {
        "taste": ["average", "plain", "acceptable", "standard"],
        "texture": ["soft enough", "average", "typical", "al dente-ish"],
    },
    "Breakfast Foods": {
        "taste": ["standard", "mild", "average", "typical"],
        "texture": ["soft", "average", "acceptable", "ordinary"],
    },
    "Electronics & Appliances": {
        "performance": ["adequate", "acceptable", "standard", "satisfactory"],
        "build": ["average", "standard", "acceptable", "adequate"],
        "usage": ["functional", "okay", "average", "acceptable"],
    },
    "Home & Living": {
        "material": ["standard", "average", "acceptable", "functional"],
        "comfort": ["moderate", "acceptable", "okay", "standard"],
        "design": ["plain", "average", "standard", "functional"],
    },
    "Sports, Travel & Leisure": {
        "experience": ["okay", "average", "moderate", "standard"],
        "durability": ["adequate", "average", "standard", "acceptable"],
        "convenience": ["acceptable", "average", "standard", "okay"],
    },
}


NEGATIVE_CATEGORY_DESCRIPTORS = {
    "Snacks": {
        "taste": ["bland", "stale", "overly salty", "too sweet", "artificial", "off"],
        "texture": [
            "soggy",
            "stale",
            "hard",
            "chewy in a bad way",
            "crumbly",
            "greasy",
        ],
    },
    "Beverages": {
        "taste": ["bitter", "watery", "flat", "too sweet", "off", "unpleasant"],
        "texture": ["thin", "watery", "foamy in a bad way", "chalky", "gritty"],
    },
    "Dairy & Eggs": {
        "taste": ["bland", "sour", "rancid", "stale", "flat", "off"],
        "texture": [
            "runny",
            "clumpy",
            "watery",
            "gritty",
            "rubbery",
            "dense in a bad way",
        ],
    },
    "Frozen Food": {
        "taste": ["bland", "frozen-tasting", "salty", "stale", "off", "oily"],
        "texture": ["frozen-hard", "chewy in a bad way", "mushy", "stale", "rubbery"],
    },
    "Fresh Produce": {
        "taste": ["bitter", "sour", "mealy", "watery", "off", "bland"],
        "texture": ["wilted", "soft in a bad way", "fibrous", "mushy", "dry"],
    },
    "Pantry Staples": {
        "taste": ["tasteless", "watery", "low-quality", "inconsistent", "not fresh"],
    },
    "Household Essentials": {
        "texture": ["rough", "flimsy", "cheap", "scratches easily", "fragile"],
        "packaging": ["hard to open", "leaky", "damaged", "bulk in a bad way"],
    },
    "Health & Beauty": {
        "texture": ["greasy", "sticky", "runny", "thin", "unpleasant"],
        "scent": [
            "strong in a bad way",
            "chemical",
            "artificial",
            "off-putting",
            "unpleasant",
        ],
    },
    "Baby Products": {
        "texture": ["rough", "scratchy", "absorbent in a bad way", "cheap"],
        "scent": ["strong", "chemical", "off", "unpleasant"],
    },
    "Canned Goods": {
        "taste": ["bland", "sour", "metallic", "too salty", "off"],
        "texture": ["mushy", "too soft", "chunky in a bad way", "watery"],
    },
    "Personal Care": {
        "texture": ["greasy", "thin", "sticky", "watery", "unpleasant"],
        "scent": ["overpowering", "chemical", "strong", "unpleasant"],
    },
    "Meat & Seafood": {
        "taste": ["gamey", "bland", "sour", "overcooked", "off"],
        "texture": ["tough", "dry", "rubbery", "chewy in a bad way", "stringy"],
    },
    "Bakery": {
        "taste": ["stale", "bland", "too sweet", "dry", "off", "flat"],
        "texture": [
            "dry",
            "crumbly in a bad way",
            "hard",
            "dense",
            "chewy in a bad way",
        ],
    },
    "Cleaning Supplies": {
        "texture": ["harsh", "abrasive", "slimy", "chemical", "rough"],
        "scent": ["overpowering", "chemical", "strong", "unpleasant"],
    },
    "Rice & Noodles": {
        "taste": ["bland", "starchy", "underseasoned", "overcooked", "off"],
        "texture": ["mushy", "sticky", "too firm", "dry", "clumpy"],
    },
    "Breakfast Foods": {
        "taste": ["bland", "overly sweet", "stale", "off", "mediocre"],
        "texture": ["soggy", "dense", "rubbery", "dry", "chewy in a bad way"],
    },
    "Electronics & Appliances": {
        "performance": ["slow", "laggy", "unresponsive", "inefficient", "fragile"],
        "build": ["flimsy", "cheap", "brittle", "unstable", "fragile"],
        "usage": ["complicated", "confusing", "frustrating", "inconvenient"],
    },
    "Home & Living": {
        "functionality": ["impractical", "inconvenient", "unsatisfactory"],
        "build": ["cheap", "not a good quality"],
        "design": [
            "clunky",
            "bulky",
            "unappealing",
            "poorly designed",
            "outdated",
            "too small",
        ],
    },
    "Sports, Travel & Leisure": {
        "performance": [
            "unreliable",
            "underperforming",
            "frustrating",
            "difficult",
            "underwhelming",
            "disappointing",
        ],
        "durability": ["fragile", "short-lived", "poorly made", "breaks easily"],
        "mobility": ["cumbersome", "heavy", "awkward to carry", "inconvenient"],
    },
}


POSITIVE_DESCRIPTOR_TEMPLATES = {
    "price": [
        "At ${value}, I think it's worth considering.",
        "Price-wise, ${value} seems fair for what you get.",
        "For ${value}, this is a good deal.",
        "Considering the quality, ${value} is reasonable.",
        "${value} feels like a worthwhile investment.",
        "The cost of ${value} is justified by its performance.",
    ],
    "taste": [
        "The taste is quite ${value}.",
        "I really noticed the ${value} flavor of ${product}.",
        "Tastes ${value}, just as expected.",
        "${product} has a ${value} flavor that's enjoyable.",
        "Really loved the ${value} taste in this one.",
        "The ${value} flavor is prominent and appealing.",
        "I found the taste to be pleasantly ${value}.",
        "${product} delivers a ${value} flavor experience.",
    ],
    "texture": [
        "The texture is ${value}.",
        "I found ${product} ${value} when using it.",
        "Feels ${value} and pleasant to use.",
        "Has a ${value} consistency that feels nice.",
        "The ${value} texture really stands out.",
        "Texture is ${value}, which I enjoyed.",
        "Really ${value} texture overall.",
    ],
    "scent": [
        "${product} smells ${value}.",
        "The ${value} scent is noticeable.",
        "Has a ${value} aroma that I liked.",
        "The ${value} fragrance adds to the overall experience.",
        "A subtle ${value} scent is present and pleasant.",
        "${product} gives off a ${value} smell that's enjoyable.",
        "The ${value} aroma is appealing and refreshing.",
        "Really appreciated the ${value} scent in this product.",
    ],
    "performance": [
        "Performance-wise, it's very ${value}.",
        "It performs ${value} for its category.",
        "Really impressed by how ${value} it is.",
        "The ${product} is ${value} in operation.",
        "Handles tasks in a ${value} manner.",
    ],
    "build": [
        "The build quality feels ${value}.",
        "Feels ${value} and solid in hand.",
        "Really well-built and ${value}.",
        "Has a ${value} construction.",
        "${product} is sturdy and ${value}.",
    ],
    "usage": [
        "Very ${value} to operate.",
        "Found it ${value} for daily use.",
        "Designed to be ${value}.",
        "Using the ${product} is quite ${value}.",
        "Offers a ${value} experience.",
    ],
    "material": [
        "Made from ${value} materials.",
        "The ${value} feel is evident.",
        "Constructed with ${value} components.",
        "Has a ${value} texture.",
        "The material quality is ${value}.",
    ],
    "comfort": [
        "Extremely ${value} to use.",
        "Offers a ${value} experience.",
        "Designed for ${value}.",
        "The ${product} provides ${value}.",
        "Feels ${value} during use.",
    ],
    "design": [
        "Features a ${value} design.",
        "The ${value} look is appealing.",
        "Has a ${value} aesthetic.",
        "The design of ${product} is quite ${value}.",
        "Showcases a ${value} style.",
    ],
    "experience": [
        "Provides an ${value} experience.",
        "Using it was quite ${value}.",
        "Overall, an ${value} product.",
        "The ${product} offers an ${value} usage.",
        "Had an ${value} time with it.",
    ],
    "durability": [
        "Very ${value} over time.",
        "Built to be ${value}.",
        "Shows ${value} after extended use.",
        "The ${product} is known for its ${value}.",
        "Offers ${value} in daily wear and tear.",
    ],
    "convenience": [
        "Extremely ${value} to carry around.",
        "Designed for ${value}.",
        "Offers ${value} in usage.",
        "The ${product} is quite ${value}.",
        "Provides ${value} for users.",
    ],
    "packaging": [
        " The packaging was ${value}.",
        " I liked how the item was ${value}.",
        " Packaged ${value}, very convenient.",
    ],
    "promotion": [
        " I got it during a ${value}, which was nice.",
        " Took advantage of the ${product} ${value} deal.",
        " Purchased it with a ${value} offer.",
    ],
}


NEGATIVE_DESCRIPTOR_TEMPLATES = {
    "price": [
        "At ${value}, not worth it.",
        "Price-wise, ${value} feels overpriced.",
        "Too expensive at ${value} for what it offers.",
        "Considering the quality, ${value} is not reasonable.",
        "${value} is not a good investment.",
    ],
    "taste": [
        "The taste is ${value} and disappointing.",
        "I found ${product}'s flavor to be ${value}, not enjoyable.",
        "Tastes ${value}, which I disliked.",
        "${product} has a ${value} flavor that I cannot recommend.",
    ],
    "texture": [
        "The texture is ${value} and unpleasant.",
        "Found ${product} ${value} when using it. Not good.",
        "Feels ${value} in a bad way.",
        "Texture is ${value}, which I disliked.",
    ],
    "scent": [
        "${product} smells ${value} and off-putting.",
        "The ${value} scent is too strong or unpleasant.",
        "Has a ${value} aroma I did not like.",
    ],
    "performance": [
        "Performance-wise, it's ${value} and frustrating.",
        "It performs ${value}, not satisfactory.",
        "The ${product} is ${value} in operation.",
    ],
    "build": [
        "The build quality is ${value} and fragile.",
        "Feels ${value} and poorly constructed.",
        "${product} is ${value} and cheap.",
    ],
    "usage": [
        "Very ${value} to operate, frustrating to use.",
        "Found it ${value} for daily use, not convenient.",
        "Using ${product} is quite ${value}, disappointing.",
    ],
    "material": [
        "Made from ${value} materials, low-quality.",
        "The ${value} feel is unpleasant.",
        "Constructed with ${value} components, feels cheap.",
    ],
    "comfort": [
        "Extremely ${value} to use, uncomfortable.",
        "Offers a ${value} experience, not pleasant.",
        "${product} provides ${value}, disappointing.",
    ],
    "design": [
        "Features a ${value} design, unattractive.",
        "The ${value} look is unappealing.",
        "Has a ${value} style that is impractical.",
    ],
    "experience": [
        "Provides a ${value} experience, not enjoyable.",
        "Using it was ${value}, frustrating overall.",
        "${product} offers a ${value} usage, disappointing.",
    ],
    "durability": [
        "Very ${value}, breaks easily.",
        "Built to be ${value}, not lasting.",
        "Shows ${value} after short use.",
    ],
    "convenience": [
        "Extremely ${value} to carry around, inconvenient.",
        "Designed for ${value}, hard to use.",
        "${product} is ${value}, not user-friendly.",
    ],
    "packaging": [
        "The packaging was ${value}, not satisfactory.",
        "Item was ${value} packed, poorly handled.",
        "Packaging felt ${value}, disappointing.",
    ],
    "promotion": [
        "Got it during a ${value}, but not worth it.",
        "The ${product} ${value} deal was disappointing.",
        "Purchased with ${value}, felt like a bad deal.",
    ],
}


POSITIVE_ADJECTIVES = [
    "excellent",
    "amazing",
    "great",
    "fantastic",
    "high-quality",
    "perfect",
    "superb",
    "wonderful",
    "impressive",
    "top-notch",
    "outstanding",
]


NEGATIVE_ADJECTIVES = [
    "disappointing",
    "poor",
    "terrible",
    "low-quality",
    "bad",
    "unsatisfactory",
    "inferior",
    "flawed",
    "subpar",
    "mediocre",
    "unpleasant",
]


NEUTRAL_PHRASES = [
    "average",
    "okay",
    "fine",
    "nothing special",
    "acceptable",
    "decent",
    "passable",
    "satisfactory",
    "moderate",
    "so-so",
]


POSITIVE_VERBS = [
    "love",
    "enjoyed",
    "liked",
    "appreciated",
    "recommend",
    "adore",
    "favor",
    "admire",
    "cherish",
    "value",
]


NEGATIVE_VERBS = [
    "disliked",
    "regret buying",
    "was unhappy with",
    "would not buy again",
    "complain about",
    "detest",
    "cannot recommend",
    "feel let down by",
    "avoid",
    "beware of",
]


NEUTRAL_VERBS = ["found", "tried", "tested", "used", "experienced"]


CATEGORY_CAMPAIGN_PROBABILITY = {
    "Snacks": 0.15,
    "Beverages": 0.12,
    "Dairy & Eggs": 0.05,
    "Frozen Food": 0.04,
    "Fresh Produce": 0.02,
    "Pantry Staples": 0.01,
    "Household Essentials": 0.01,
    "Health & Beauty": 0.05,
    "Baby Products": 0.03,
    "Canned Goods": 0.02,
    "Personal Care": 0.05,
    "Meat & Seafood": 0.03,
    "Bakery": 0.04,
    "Cleaning Supplies": 0.01,
    "Rice & Noodles": 0.01,
    "Breakfast Foods": 0.03,
    "Electronics & Appliances": 0.10,
    "Home & Living": 0.05,
    "Sports, Travel & Leisure": 0.08,
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


SEASONAL_DATES = {
    "CNY": (datetime(2024, 2, 10), datetime(2024, 2, 17)),
    "Christmas": (datetime(2024, 12, 22), datetime(2024, 12, 28)),
    "Black Friday": (datetime(2024, 11, 26), datetime(2024, 12, 2)),
    "1111": (datetime(2024, 11, 8), datetime(2024, 11, 14)),
    "1212": (datetime(2024, 12, 9), datetime(2024, 12, 15)),
}


SEASON_PEAK_CATEGORIES = {
    "CNY": [
        "Beverages",
        "Frozen Food",
        "Lifestyle & Recreation",
        "Meat & Seafood",
        "Rice & Noodles",
        "Snacks",
    ],
    "Christmas": [
        "Bakery",
        "Beverages",
        "Dairy & Eggs",
        "Electronics & Appliances",
        "Sports, Travel & Leisure",
        "Meat & Seafood",
    ],
    "Black Friday": [
        "Electronics & Appliances",
        "Home & Living",
        "Sports, Travel & Leisure",
    ],
    "1111": [
        "Electronics & Appliances",
        "Home & Living",
        "Sports, Travel & Leisure",
    ],
    "1212": [
        "Electronics & Appliances",
        "Home & Living",
        "Sports, Travel & Leisure",
    ],
}


SEASON_CODE_MAP = {
    "CNY": "CNY",
    "Christmas": "XMAS",
    "Black Friday": "BF",
    "1111": "1111",
    "1212": "1212",
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


CHANNEL_CONSENT_MAP = {
    "Email": "email_marketing_opt_in",
    "SMS": "sms_marketing_opt_in",
    "Push Notifications": "push_notifications_opt_in",
}


CAMPAIGN_SESSION_FREQUENCY = {
    "treatment": 1.3,
    "control": 1,
    "non-campaign": 1,
}


CART_SIZE_BY_SEGMENT = {
    "New Customers": 0.5,
    "Active Customers": 1.5,
    "High Spenders": 3.0,
    "Budget Shoppers": 2.0,
    "Churn Risk Customers": 0.7,
}


CATEGORY_FREQUENCY = {
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


DAY_WEIGHTS = {"Weekday": 0.65, "Weekend": 0.35}


HOUR_WEIGHTS = {
    "Midnight": (0, 6, 0.05),  # 12am–6am
    "Daytime": (6, 18, 0.25),  # 6am–6pm
    "Evening": (18, 22, 0.6),  # 6pm–10pm
    "Late": (22, 24, 0.1),  # 10pm-12am
}


LANDING_PAGE_BEHAVIOUR = {
    "direct": {
        "Home View": 0.70,
        "Search View": 0.30,
    },
    "email_campaign": {
        "Home View": 0.85,
        "Category View": 0.15,
    },
    "google.com": {
        "Search View": 0.60,
        "Home View": 0.20,
        "Product View": 0.20,
    },
    "facebook.com": {
        "Product View": 0.80,
        "Home View": 0.20,
    },
    "instagram.com": {
        "Product View": 0.80,
        "Home View": 0.20,
    },
    "tiktok.com": {
        "Product View": 0.80,
        "Home View": 0.20,
    },
    "youtube.com": {
        "Product View": 0.80,
        "Home View": 0.20,
    },
    "shopee.sg": {
        "Product View": 0.80,
        "Home View": 0.20,
    },
    "lazada.sg": {
        "Product View": 0.80,
        "Home View": 0.20,
    },
    "telegram.org": {
        "Product View": 0.80,
        "Home View": 0.20,
    },
}


REFERRER_DISTRIBUTION = {
    "google.com": 0.55,
    "facebook.com": 0.2,
    "instagram.com": 0.06,
    "tiktok.com": 0.05,
    "youtube.com": 0.04,
    "direct": 0.04,
    "email_campaign": 0.03,
    "telegram.org": 0.01,
    "shopee.sg": 0.01,
    "lazada.sg": 0.01,
}


SEASONAL_UPLIFT = {
    "Daytime": {
        "extra_events": (0, 1),
        "session_mult": (0.95, 1.05),
        "atc_mult": (0.98, 1.02),
        "checkout_mult": (0.98, 1.02),
        "conversion_mult": (0.98, 1.02),
    },
    "Evening": {
        "extra_events": (1, 3),
        "session_mult": (1.15, 1.35),
        "atc_mult": (1.05, 1.12),
        "checkout_mult": (1.05, 1.1),
        "conversion_mult": (1.05, 1.12),
    },
    "Weekday": {
        "extra_events": (0, 1),
        "session_mult": (0.95, 1.05),
        "atc_mult": (1.08, 1.02),
        "checkout_mult": (1.08, 1.12),
        "conversion_mult": (1.08, 1.02),
    },
    "Weekend": {
        "extra_events": (1, 3),
        "session_mult": (1.2, 1.45),
        "atc_mult": (1.1, 1.2),
        "checkout_mult": (1.08, 1.15),
        "conversion_mult": (1.1, 1.18),
    },
    "Payday": {
        "extra_events": (2, 4),
        "session_mult": (1.15, 1.3),
        "atc_mult": (1.15, 1.25),
        "checkout_mult": (1.12, 1.2),
        "conversion_mult": (1.15, 1.3),
    },
    "Payday spillover": {
        "extra_events": (1, 3),
        "session_mult": (1.1, 1.2),
        "atc_mult": (1.1, 1.2),
        "checkout_mult": (1.08, 1.15),
        "conversion_mult": (1.1, 1.18),
    },
    "CNY": {
        "extra_events": (3, 6),
        "session_mult": (1.25, 1.5),
        "atc_mult": (1.2, 1.4),
        "checkout_mult": (1.3, 1.6),
        "conversion_mult": (1.5, 2.2),
    },
    "Christmas": {
        "extra_events": (3, 6),
        "session_mult": (1.3, 1.55),
        "atc_mult": (1.25, 1.5),
        "checkout_mult": (1.4, 1.8),
        "conversion_mult": (1.6, 2.5),
    },
    "1111": {
        "extra_events": (5, 10),
        "session_mult": (1.6, 2),
        "atc_mult": (1.5, 2),
        "checkout_mult": (1.8, 2.5),
        "conversion_mult": (2, 3.5),
    },
    "1212": {
        "extra_events": (5, 10),
        "session_mult": (1.6, 2),
        "atc_mult": (1.5, 2),
        "checkout_mult": (1.8, 2.5),
        "conversion_mult": (2, 3.5),
    },
}


SEGMENT_SESSION_FREQUENCY = {
    "New Customers": 1.2,
    "Active Customers": 1.4,
    "Churn Risk Customers": 0.3,
    "High Spenders": 1,
    "Budget Shoppers": 1.1,
}


TIME_ON_PAGE = {
    "Home View": (3, 8, 25),
    "Category View": (5, 12, 40),
    "Search View": (5, 15, 35),
    "Product View": (10, 25, 80),
    "Add to Cart": (3, 10, 30),
    "Cart View": (5, 20, 60),
    "Remove from Cart": (2, 6, 20),
    "Checkout Start": (10, 30, 120),
    "Payment Attempt": (5, 40, 180),
    "Payment Successful": (2, 4, 10),
    "Payment Failed": (2, 6, 30),
}


VALID_EVENT_TRANSITIONS = {
    "Home View": {
        "Product View": 0.4,
        "Category View": 0.3,
        "Search View": 0.25,
        "Cart View": 0.05,
    },
    "Category View": {
        "Product View": 0.45,
        "Search View": 0.3,
        "Home View": 0.2,
        "Cart View": 0.05,
    },
    "Search View": {
        "Product View": 0.5,
        "Category View": 0.3,
        "Home View": 0.2,
    },
    "Product View": {
        "Category View": 0.35,
        "Home View": 0.3,
        "Search View": 0.15,
        "Add to Cart": 0.15,
        "Cart View": 0.05,
    },
    "Add to Cart": {
        "Cart View": 0.4,
        "Product View": 0.3,
        "Category View": 0.2,
        "Remove from Cart": 0.1,
    },
    "Cart View": {
        "Checkout Start": 0.6,
        "Remove from Cart": 0.2,
        "Product View": 0.1,
        "Category View": 0.1,
    },
    "Remove from Cart": {
        "Cart View": 0.5,
        "Product View": 0.2,
        "Category View": 0.2,
        "Home View": 0.1,
    },
    "Checkout Start": {
        "Payment Attempt": 0.9,
        "Remove from Cart": 0.1,
    },
    "Payment Attempt": {
        "Payment Successful": 0.8,
        "Payment Failed": 0.2,
    },
    "Payment Successful": {
        "Home View": 0.2,
    },
    "Payment Failed": {
        "Home View": 0.7,
        "Payment Attempt": 0.3,
    },
}
