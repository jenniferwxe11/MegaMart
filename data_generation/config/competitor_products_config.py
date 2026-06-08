from typing import Tuple, TypedDict


class CompetitorConfig(TypedDict):
    price_bias: Tuple[float, float]
    promo_rate: float
    category_noise: float
    name_noise: float


CATEGORY_TO_COMPETITOR = {
    "Beverages": [
        "Drinks",
        "Beverages",
    ],
    "Snacks": [
        "Snack Food",
        "Snacks & Confectionery",
    ],
    "Fresh Produce": [
        "Fresh Vegetables",
        "Fresh Food",
        "Fresh",
        "Groceries",
        "Fresh & Chilled",
    ],
    "Frozen Food": [
        "Frozen",
        "Chilled & Frozen",
    ],
    "Household Essentials": [
        "Household",
        "Home Care",
        "Household Needs",
    ],
    "Personal Care": [
        "Personal Hygiene",
    ],
    "Meat & Seafood": [
        "Fresh Meat",
        "Seafood",
        "Fresh & Chilled",
    ],
    "Pantry Staples": ["Pantry"],
    "Baby Products": [
        "Baby & Maternity",
    ],
    "Dairy & Eggs": [
        "Fresh & Chilled",
    ],
}


COMPETITOR_CATEGORIES = {
    "Sheng Shiong": [
        "Fresh Vegetables",
        "Fresh Meat",
        "Seafood",
        "Rice & Noodles",
        "Drinks",
        "Snack Food",
        "Household Essentials",
        "Personal Hygiene",
        "Festive Goods",
        "Bulk Staples",
    ],
    "Fairprice": [
        "Fresh Food",
        "Chilled & Frozen",
        "Alcoholic Beverages",
        "Snacks & Confectionery",
        "Ready-to-Eat",
        "Health Products",
        "Baby & Maternity",
        "Home Care",
        "Pet Care",
    ],
    "Giant": [
        "Fresh & Chilled",
        "Pantry",
        "Frozen",
        "Drinks",
        "Snacks",
        "Household Needs",
        "Personal Care",
        "Party Supplies",
    ],
    "RedMart": [
        "Fresh",
        "Chilled",
        "Frozen",
        "Pantry",
        "Beverages",
        "Organic & Natural",
        "International Foods",
        "Gourmet",
        "Pet Supplies",
    ],
    "GrabMart": [
        "Groceries",
        "Convenience Items",
        "Ready Meals",
        "Drinks",
        "Late Night Essentials",
        "Health & Pharmacy",
    ],
}


COMPETITOR_CATEGORY_ITEMS = {
    "Alcoholic Beverages": [
        "Beer",
    ],
    "Convenience Items": [
        "Instant Cup Noodles",
        "Bottled Drinks",
        "Packaged Sandwich",
        "Energy Bar",
        "Microwavable Rice",
    ],
    "Ready-to-Eat": [
        "Microwavable Meals",
        "Bento Sets",
        "Hot Snacks",
        "Ready Pasta",
        "Rice Bowls",
    ],
    "Ready Meals": [
        "Microwavable Meals",
        "Bento Sets",
        "Hot Snacks",
        "Ready Pasta",
        "Rice Bowls",
    ],
    "Bulk Staples": [
        "Rice",
        "Bulk Cooking Oil",
        "Large Sugar Pack",
        "Bulk Flour",
    ],
    "Chilled": [
        "Chilled Juice",
        "Chilled Desserts",
        "Fresh Milk",
        "Yogurt Cups",
    ],
    "Gourmet": [
        "Truffle Oil",
        "Imported Cheese",
        "Premium Chocolate",
        "Artisan Pasta",
    ],
    "Organic & Natural": [
        "Organic Eggs",
        "Organic Vegetables",
        "Natural Peanut Butter",
        "Organic Juice",
    ],
    "Late Night Essentials": [
        "Malt Drinks",
        "Energy Drinks",
        "Ice Cream",
        "Frozen Snacks",
        "Snack Bars",
    ],
    "Festive Goods": [
        "Mandarin Oranges",
        "Turkey",
        "Festive Cookies",
        "Gift Hampers",
    ],
    "Pet Care": [
        "Dry Dog Food",
        "Cat Litter",
        "Pet Snacks",
        "Pet Shampoo",
    ],
    "Pet Supplies": [
        "Dry Dog Food",
        "Cat Litter",
        "Pet Snacks",
        "Pet Shampoo",
    ],
    "Party Supplies": [
        "Disposable Plates",
        "Party Decorations",
        "Balloons",
        "Party Poppers",
        "Candles",
    ],
    "International Foods": [
        "Japanese Snacks",
        "Japanese Ramen",
        "Soba",
        "Cup Noodles",
        "Udon",
        "Teriyaki Sauce",
    ],
    "Health Products": [
        "Vitamin C",
        "Fish Oil",
        "Multivitamins",
        "Herbal Supplements",
    ],
    "Health & Pharmacy": [
        "Antacid",
        "Painkiller",
        "Antiseptic Cream",
        "Cough & Flu",
        "Allergy Medicine",
        "Throat Lozenges",
        "Eye Drops",
    ],
}


COMPETITOR_BRANDS = {
    "Alcoholic Beverages": [
        "Tiger Beer",
        "Heineken",
        "Carlsberg",
        "Somersby",
        "Jacob's Creek",
    ],
    "Ready-to-Eat": [
        "FairPrice Kitchen",
        "CP Ready Meals",
    ],
    "Ready Meals": [
        "7-Eleven",
        "CP",
        "Prima Taste",
        "Myojo",
    ],
    "Convenience Items": [
        "7-Eleven",
        "Cheers",
        "Scarlet Supermarket",
    ],
    "Late Night Essentials": [
        "Nestle",
        "Milo",
        "Walls",
    ],
    "Chilled": [
        "Meiji",
        "Farmhouse",
        "Marigold",
    ],
    "Organic & Natural": [
        "Little Farms",
        "Nature's Wonders",
        "Organic Valley",
    ],
    "Gourmet": [
        "Marks & Spencer",
        "Waitrose",
        "La Molisana",
    ],
    "International Foods": [
        "Nissin",
        "Ottogi",
        "Kikkoman",
    ],
    "Health Products": [
        "Blackmores",
        "Swisse",
        "Nature Made",
    ],
    "Health & Pharmacy": [
        "Panadol",
        "Strepsils",
        "Zyrtec",
    ],
    "Pet Care": [
        "Pedigree",
        "Whiskas",
        "Royal Canin",
    ],
    "Pet Supplies": [
        "Pedigree",
        "Whiskas",
        "Royal Canin",
    ],
    "Party Supplies": [
        "Party City",
        "Unique Party",
        "Funlah",
    ],
    "Festive Goods": [
        "Sheng Shiong Festive",
        "Sheng Shiong Seasonal",
    ],
    "Bulk Staples": [
        "Golden Chef",
        "Knife",
        "Daily Essentials",
    ],
}


COMPETITOR_CATEGORY_PRICE_RANGES = {
    "Convenience Items": (1.50, 6.00),
    "Ready-to-Eat": (4.50, 12.00),
    "Ready Meals": (4.50, 12.00),
    "Bulk Staples": (6.00, 25.00),
    "Alcoholic Beverages": (5.00, 15.00),
    "Organic & Natural": (4.00, 20.00),
    "Gourmet": (12.00, 30.00),
    "Chilled": (3.00, 10.00),
    "International Foods": (3.50, 18.00),
    "Health Products": (8.00, 45.00),
    "Health & Pharmacy": (5.00, 25.00),
    "Pet Care": (6.00, 35.00),
    "Pet Supplies": (6.00, 35.00),
    "Party Supplies": (2.00, 15.00),
    "Festive Goods": (5.00, 60.00),
    "Late Night Essentials": (2.00, 8.00),
    "Fresh Produce": (1.00, 12.00),
    "Meat & Seafood": (3.00, 25.00),
    "Dairy & Eggs": (2.00, 10.00),
    "Snacks": (1.00, 8.00),
    "Beverages": (1.00, 12.00),
    "Pantry Staples": (2.00, 20.00),
}


COMPETITOR_EXCLUSIVE_BRANDS = {
    "Fairprice": [
        "FairPrice Housebrand",
        "Pasar FairPrice",
        "Meadows",
    ],
    "Sheng Shiong": [
        "Sheng Siong Select",
        "Happy Family",
    ],
    "RedMart": [
        "RedMart House",
        "Marks & Spencer",
        "Waitrose",
    ],
    "Giant": [
        "Giant Value",
        "Nature's Promise",
    ],
    "GrabMart": [
        "GrabKitchen",
        "Local Hawker Partner",
    ],
}


COMPETITOR_EXCLUSIVE_BRAND_BIAS = {
    "Sheng Shiong": 0.05,
    "Fairprice": 0.50,
    "Giant": 0.20,
    "RedMart": 0.10,
    "GrabMart": 0.05,
}


NAME_PATTERNS = [
    "{brand} {product}",
    "{product}",
    "{product} - {brand}",
    "{brand} - {product}",
    "{product} ({brand})",
    "{brand} ({product})",
    "{product} | {brand}",
    "[{brand}] {product}",
    "{product} [{brand}]",
]


COMPETITORS: dict[str, CompetitorConfig] = {
    "Fairprice": {
        "price_bias": (-0.08, 0.08),
        "promo_rate": 0.35,
        "category_noise": 0.25,
        "name_noise": 0.35,
    },
    "Sheng Shiong": {
        "price_bias": (-0.15, -0.02),  # cheaper
        "promo_rate": 0.25,
        "category_noise": 0.3,
        "name_noise": 0.4,
    },
    "Giant": {
        "price_bias": (-0.1, 0.1),
        "promo_rate": 0.30,
        "category_noise": 0.35,
        "name_noise": 0.4,
    },
    "RedMart": {
        "price_bias": (0.05, 0.2),  # more expensive
        "promo_rate": 0.2,
        "category_noise": 0.2,
        "name_noise": 0.25,
    },
    "GrabMart": {
        "price_bias": (0.1, 0.3),  # convenience premium
        "promo_rate": 0.4,
        "category_noise": 0.4,
        "name_noise": 0.45,
    },
}


TERM_SWAPS = {
    # variant/descriptor
    "Original": ["Classic", "Regular"],
    "Organic": ["Natural", "Pure"],
    "Family Pack": ["Value Pack", "Large Pack"],
    "Heavy Duty": ["Strong", "Powerful"],
    "Portable": ["Lightweight"],
    "Compact": ["Mini", "Small"],
    "Eco-Friendly": ["Green", "Sustainable"],
    "Gluten-Free": ["Wheat-Free", "Celiac-Friendly"],
    "Low Sugar": ["Reduced Sugar", "Sugar-Free"],
    "Reduced Salt": ["Light Salt", "Low Sodium"],
    "Sensitive": ["Gentle", "Mild"],
    "Whitening": ["Brightening", "Lightening"],
    "Cooling": ["Refreshing", "Chill"],
    "Travel Size": ["Mini", "Pocket Size"],
    "Premium": ["Deluxe", "Superior"],
    "Imported": ["Overseas", "International"],
    "Local": ["Domestic", "Homegrown"],
    "Value": ["Economy", "Budget"],
    "Chocolate": ["Choco", "Cocoa"],
    "Honey": ["Sweet", "Golden"],
    "Salted": ["Salty", "Sea Salt"],
    "Zero Sugar": ["Sugar-Free", "No Sugar"],
    "Less Sugar": ["Reduced Sugar", "Light Sugar"],
    "Concentrate": ["Syrup", "Essence"],
    # net content/sizes
    "50g": ["0.05kg"],
    "100g": ["0.1kg"],
    "150g": ["0.15kg"],
    "200g": ["0.2kg"],
    "250g": ["0.25kg"],
    "300g": ["0.3kg"],
    "400g": ["0.4kg"],
    "500g": ["0.5kg"],
    "800g": ["0.8kg"],
    "1kg": ["1000g"],
    "330ml": ["0.33L"],
    "500ml": ["0.5L"],
    "1L": ["1000ml"],
    "1.5L": ["1500ml"],
    "Loose": ["Bulk", "Unpackaged"],
    # colour
    "White": ["Off-White", "Ivory"],
    "Black": ["Dark", "Onyx"],
    "Grey": ["Silver", "Charcoal"],
    # pack quantity
    "2-pack": ["Pack of 2", "Double Pack"],
    "4-pack": ["Pack of 4", "Quad Pack"],
    "6-pack": ["Pack of 6", "Hexa Pack"],
    "12-pack": ["Pack of 12", "Dozen Pack"],
    "24-pack": ["Pack of 24", "Two Dozen Pack"],
}
