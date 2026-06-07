from typing import Any, Dict, List

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
    "Fresh Produce": ["Dole", "Zespri", "Zenxin Organic Food", "Little Farms"],
    "Pantry Staples": [
        "Knife",
        "Lee Kum Kee",
        "Ayam Brand",
        "San Remo",
        "Golden Farm",
        "Maggie",
        "A1",
    ],
    "Household Essentials": ["Kleenex", "Hada", "Premier"],
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


CATEGORY_PRICE_RANGES = {
    # Per 100g/100ml
    "Snacks": (0.5, 1.2),
    "Beverages": (0.2, 0.8),
    "Frozen Food": (0.7, 1.8),
    "Fresh Produce": (0.8, 2.5),
    "Health & Beauty": (1.5, 5.0),
    "Canned Goods": (0.6, 1.8),
    "Personal Care": (2.5, 5.5),
    "Meat & Seafood": (1.5, 5.5),
    "Cleaning Supplies": (0.3, 0.8),
    "Breakfast Foods": (0.6, 2.2),
    "Rice & Noodles": (0.5, 1.2),
    # Per pack
    "Dairy & Eggs": (2.5, 6.0),
    "Bakery": (1.5, 4.0),
    "Household Essentials": (2.0, 6.0),
    # Per item
    "Pantry Staples": (2.0, 10.0),
    "Baby Products": (10.0, 35.0),
    "Electronics & Appliances": (40.0, 300.0),
}


# Price per unit max
PACK_PRICE_CAP = {
    "Beverages": (1.2, 2.5),
    "Snacks": (0.8, 2.0),
    "Dairy & Eggs": (2.0, 5.0),
}


SUBCATEGORY_PRICE_RANGES = {
    "Kitchenware": (10.0, 40.0),
    "Storage & Organization": (10.0, 40.0),
    "Bedding & Furnishings": (20.0, 100.0),
    "Fitness & Wellness": (15.0, 80.0),
    "Travel Gear": (30.0, 180.0),
    "Games & Hobbies": (8.0, 30.0),
    "Outdoor Equipment": (50.0, 250.0),
}


ITEM_PRICE_RANGES = {
    # Electronics
    "Refrigerator": (400.0, 1200.0),
    "Microwave": (80.0, 250.0),
    "Washing Machine": (400.0, 900.0),
    # Kitchenware
    "Cookware": (30.0, 100.0),
    "Water Bottles": (8.0, 30.0),
    "Food Containers": (8.0, 30.0),
    "Cutleries": (10.0, 35.0),
    # Storage
    "Storage Boxes": (10.0, 35.0),
    "Wardrobe Organizers": (15.0, 60.0),
    "Shelving Units": (60.0, 180.0),
    # Fitness
    "Dumbbells": (25.0, 120.0),
    "Yoga Mat": (12.0, 35.0),
    "Resistance Bands": (10.0, 30.0),
    # Travel
    "Suitcase": (80.0, 250.0),
    "Backpack": (30.0, 100.0),
    "Travel Pillow": (10.0, 25.0),
    # Outdoor
    "Camping Tent": (100.0, 300.0),
    "Sleeping Bag": (50.0, 150.0),
}


CATEGORY_MIN_PRICE = {
    "Snacks": 0.60,
    "Beverages": 0.80,
    "Fresh Produce": 0.70,
    "Canned Goods": 1.00,
    "Rice & Noodles": 1.00,
    "Pantry Staples": 2.00,
    "Bakery": 1.50,
    "Dairy & Eggs": 2.50,
    "Personal Care": 3.00,
    "Health & Beauty": 4.00,
    "Cleaning Supplies": 2.00,
    "Baby Products": 10.00,
    "Meat & Seafood": 6.00,
    "Home & Living": 10.00,
    "Sports, Travel & Leisure": 15.00,
    "Electronics & Appliances": 50.00,
}


# Cost price as % of selling price
CATEGORY_COST_MARGIN = {
    "Snacks": (0.5, 0.75),
    "Beverages": (0.5, 0.75),
    "Dairy & Eggs": (0.6, 0.85),
    "Frozen Food": (0.6, 0.85),
    "Fresh Produce": (0.4, 0.7),
    "Pantry Staples": (0.6, 0.85),
    "Household Essentials": (0.6, 0.85),
    "Health & Beauty": (0.6, 0.9),
    "Baby Products": (0.55, 0.85),
    "Canned Goods": (0.5, 0.8),
    "Personal Care": (0.6, 0.9),
    "Meat & Seafood": (0.6, 0.8),
    "Bakery": (0.5, 0.75),
    "Cleaning Supplies": (0.6, 0.85),
    "Rice & Noodles": (0.6, 0.85),
    "Breakfast Foods": (0.6, 0.85),
    "Electronics & Appliances": (0.75, 0.95),
    "Home & Living": (0.65, 0.9),
    "Sports, Travel & Leisure": (0.65, 0.9),
}


CATEGORY_PRODUCT_DISTRIBUTION = {
    # Mature categories (high SKU density)
    "Snacks": 0.12,
    "Beverages": 0.10,
    "Dairy & Eggs": 0.08,
    "Frozen Food": 0.08,
    "Health & Beauty": 0.08,
    # Mid-depth categories
    "Canned Goods": 0.06,
    "Meat & Seafood": 0.06,
    "Personal Care": 0.05,
    "Electronics & Appliances": 0.06,
    "Home & Living": 0.05,
    "Sports, Travel & Leisure": 0.05,
    # Underdeveloped categories
    "Fresh Produce": 0.03,
    "Pantry Staples": 0.03,
    "Household Essentials": 0.03,
    "Baby Products": 0.03,
    "Bakery": 0.02,
    "Cleaning Supplies": 0.02,
    "Rice & Noodles": 0.02,
    "Breakfast Foods": 0.01,
}


CATEGORY_AFFINITY = {
    "Snacks": ["Beverages", "Breakfast Foods"],
    "Beverages": ["Snacks"],
    "Dairy & Eggs": ["Bakery", "Breakfast Foods"],
    "Fresh Produce": ["Meat & Seafood", "Pantry Staples"],
    "Pantry Staples": ["Canned Goods", "Rice & Noodles"],
    "Rice & Noodles": ["Canned Goods", "Pantry Staples"],
    "Cleaning Supplies": ["Household Essentials"],
    "Household Essentials": ["Cleaning Supplies"],
    "Personal Care": ["Health & Beauty"],
    "Health & Beauty": ["Personal Care"],
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
