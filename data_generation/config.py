NUM_CUSTOMERS = 100
NUM_PHYSICAL_STORES = 5
NUM_PRODUCTS = 50
NUM_REVIEWS = 100

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
    "Home & Living (Kitchenware, Storage, Bedding)",
    "Lifestyle & Recreation (Fitness, Toys, Travel)",
]


BRANDS = {
    "Snacks": ["Lays", "Pringles", "Oreo", "Jack n Jill", "Ritz", "Nature Valley"],
    "Beverages": ["Coca-Cola", "Pepsi", "Heaven & Earth", "Nestle", "Pokka"],
    "Dairy & Eggs": ["Farmhouse", "Marigold", "Meiji", "Nestlé", "SCS"],
    "Frozen Food": ["CP", "McCain", "Farmpride", "First Pride"],
    "Fresh Produce": ["Dole", "Sunkist", "Zespri", "Local Farm"],
    "Pantry Staples": ["Knife", "Lee Kum Kee", "Ayam Brand", "San Remo", "FairPrice"],
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
    "Meat & Seafood": ["Ben's Farm", "Sadia", "Ocean Fresh", "Farmhouse"],
    "Bakery": ["Gardenia", "Sunshine", "Bimbo"],
    "Cleaning Supplies": ["Mr Muscle", "Vanish", "Ajax", "Clorox"],
    "Rice & Noodles": ["Royal Umbrella", "SongHe", "Maggi", "Koka"],
    "Breakfast Foods": ["Kellogg's", "Quaker", "Post", "Nestlé"],
    "Electronics & Appliances": [
        "Philips",
        "Xiaomi",
        "Samsung",
        "Panasonic",
        "Dyson",
    ],
    "Home & Living (Kitchenware, Storage, Bedding)": [
        "IKEA",
        "Lock&Lock",
        "Tefal",
        "Zojirushi",
        "HomeBasics",
    ],
    "Lifestyle & Recreation (Fitness, Toys, Travel)": [
        "Decathlon",
        "Nike",
        "Adidas",
        "Samsonite",
        "LEGO",
    ],
}


CATEGORY_ITEMS = {
    "Snacks": ["Chips", "Biscuits", "Bars", "Cookies", "Nuts"],
    "Beverages": ["Cola", "Juice", "Tea", "Coffee", "Soda", "Energy Drinks"],
    "Dairy & Eggs": ["Milk", "Cheese", "Butter", "Yogurt", "Cream", "Eggs"],
    "Frozen Food": ["Pizza", "Fries", "Dumplings", "Frozen Veggies", "Ice Cream"],
    "Fresh Produce": ["Apples", "Bananas", "Carrots", "Tomatoes", "Spinach"],
    "Pantry Staples": ["Cooking Oil", "Salt", "Sugar", "Flour", "Sauces", "Seasoning"],
    "Household Essentials": [
        "Toilet Paper",
        "Trash Bags",
        "Detergent Pods",
        "Soap Refills",
    ],
    "Health & Beauty": ["Toothpaste", "Lotion", "Shampoo", "Conditioner", "Body Wash"],
    "Baby Products": ["Diapers", "Wipes", "Powder", "Cream", "Formula"],
    "Canned Goods": ["Tomatoes", "Corn", "Beans", "Tuna", "Soup"],
    "Personal Care": ["Deodorant", "Shaving Foam", "Razors", "Hand Sanitizer"],
    "Meat & Seafood": ["Chicken", "Beef", "Fish", "Prawns", "Salmon", "Bacon"],
    "Bakery": ["Bread", "Cake", "Buns", "Croissant", "Muffin"],
    "Cleaning Supplies": ["Bleach", "All-purpose Spray", "Scrub Brush", "Wipes"],
    "Rice & Noodles": ["Rice", "Pasta", "Noodles", "Vermicelli", "Spaghetti"],
    "Breakfast Foods": ["Cereal", "Oats", "Granola", "Muesli", "Porridge"],
    "Electronics & Appliances": [
        "Headphones",
        "Blender",
        "Air Fryer",
        "Smartwatch",
        "Vacuum Cleaner",
    ],
    "Home & Living (Kitchenware, Storage, Bedding)": [
        "Cookware",
        "Food Containers",
        "Bedsheets",
        "Pillows",
        "Storage Boxes",
    ],
    "Lifestyle & Recreation (Fitness, Toys, Travel)": [
        "Dumbbells",
        "Yoga Mat",
        "Board Games",
        "Suitcase",
        "Sports Bottle",
    ],
}


# Approximate price ranges per category
CATEGORY_PRICE_RANGES = {
    "Snacks": (0.5, 10.0),
    "Beverages": (1.0, 8.0),
    "Dairy & Eggs": (2.0, 15.0),
    "Frozen Food": (3.0, 25.0),
    "Fresh Produce": (0.5, 5.0),
    "Pantry Staples": (1.0, 20.0),
    "Household Essentials": (2.0, 30.0),
    "Health & Beauty": (3.0, 50.0),
    "Baby Products": (5.0, 60.0),
    "Canned Goods": (1.0, 10.0),
    "Personal Care": (3.0, 40.0),
    "Meat & Seafood": (5.0, 50.0),
    "Bakery": (1.0, 15.0),
    "Cleaning Supplies": (2.0, 25.0),
    "Rice & Noodles": (1.5, 15.0),
    "Breakfast Foods": (3.0, 25.0),
    "Electronics & Appliances": (20.0, 1000.0),
    "Home & Living (Kitchenware, Storage, Bedding)": (5.0, 300.0),
    "Lifestyle & Recreation (Fitness, Toys, Travel)": (5.0, 500.0),
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
    "Home & Living (Kitchenware, Storage, Bedding)": (0.6, 0.9),
    "Lifestyle & Recreation (Fitness, Toys, Travel)": (0.6, 0.9),
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
    "Home & Living (Kitchenware, Storage, Bedding)": {
        "material": ["sturdy", "lightweight", "soft", "premium", "durable"],
        "comfort": ["comfortable", "supportive", "cozy", "soft-touch"],
        "design": ["minimalist", "modern", "practical", "space-saving"],
    },
    "Lifestyle & Recreation (Fitness, Toys, Travel)": {
        "experience": ["engaging", "fun", "effective", "challenging", "enjoyable"],
        "durability": ["sturdy", "long-lasting", "high-quality", "robust"],
        "convenience": ["portable", "easy to carry", "lightweight", "travel-friendly"],
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
    "Home & Living (Kitchenware, Storage, Bedding)": {
        "material": ["standard", "average", "acceptable", "functional"],
        "comfort": ["moderate", "acceptable", "okay", "standard"],
        "design": ["plain", "average", "standard", "functional"],
    },
    "Lifestyle & Recreation (Fitness, Toys, Travel)": {
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
    "Home & Living (Kitchenware, Storage, Bedding)": {
        "material": ["cheap", "flimsy", "rough", "low-quality", "fragile"],
        "comfort": ["uncomfortable", "unsupportive", "hard", "scratchy", "rough"],
        "design": ["awkward", "unattractive", "clunky", "impractical", "bulky"],
    },
    "Lifestyle & Recreation (Fitness, Toys, Travel)": {
        "experience": [
            "boring",
            "frustrating",
            "difficult",
            "underwhelming",
            "disappointing",
        ],
        "durability": [
            "fragile",
            "short-lived",
            "poor quality",
            "breaks easily",
            "flimsy",
        ],
        "convenience": [
            "cumbersome",
            "heavy",
            "inconvenient",
            "awkward to carry",
            "unportable",
        ],
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
