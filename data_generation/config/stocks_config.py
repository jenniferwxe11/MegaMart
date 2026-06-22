BRAND_STOCKOUT_MULTIPLIER = {
    # Snacks
    "Lays": 1.2,
    "Pringles": 0.9,
    "Oreo": 0.8,
    "Jack n Jill": 1.1,
    "Ritz": 0.9,
    "Nature Valley": 0.8,
    # Beverages
    "Coca-Cola": 0.7,
    "Pepsi": 0.8,
    "Heaven & Earth": 1.0,
    "Nestle": 0.8,
    "Pokka": 1.1,
    # Fresh Produce
    "Dole": 0.9,
    "Zespri": 0.8,
    "Zenxin Organic Food": 1.2,
    "Little Farms": 1.1,
    # Meat & Seafood
    "Kee Song": 0.8,
    "Sadia": 0.9,
    "Ocean Fresh": 1.2,
    # Electronics
    "Samsung": 0.7,
    "Dyson": 0.6,
    "Xiaomi": 1.1,
    "Toyomi": 1.2,
}


CHANGE_REASONS = {
    "stockout": "Stockout event — stock zeroed",
    "pre_stockout_drain": "Anticipated stockout — proactive drawdown",
    "seasonal_restock": "Pre-seasonal restock",
    "seasonal_drop": "Post-seasonal demand drop",
    "overstocked_reduction": "Overstocked — replenishment paused",
    "overorder": "Forecasting error — over-ordered",
    "healthy_drift": "Normal healthy-band drift",
    "low_band_drift": "Low-band minor fluctuation",
    "critical_replenish": "Critical stock — replenishment triggered",
    "critical_decay": "Critical stock — operational delay, partial decay",
    "eol_drawdown": "End-of-life — replenishment stopped",
    "eol_final_restock": "End-of-life — small final restock",
    "spoilage": "Perishable spoilage / expiry loss",
}


CATEGORY_STOCKOUT_PROB = {
    # perishable, daily replenishment risk
    "Fresh Produce": 0.30,
    "Meat & Seafood": 0.28,
    "Bakery": 0.25,
    # cold chain but stable
    "Frozen Food": 0.10,
    "Dairy & Eggs": 0.18,
    # promo-driven spikes
    "Snacks": 0.12,
    "Beverages": 0.10,
    "Breakfast Foods": 0.10,
    "Pantry Staples": 0.08,
    "Rice & Noodles": 0.06,
    "Canned Goods": 0.05,
    "Household Essentials": 0.05,
    "Cleaning Supplies": 0.06,
    "Personal Care": 0.05,
    "Health & Beauty": 0.04,
    "Baby Products": 0.04,
    # long lead time, lower volume
    "Electronics & Appliances": 0.07,
    "Home & Living": 0.06,
    "Sports, Travel & Leisure": 0.08,
}


LIFECYCLE_STOCKOUT_MULTIPLIER = {
    "New": 1.5,  # launch demand uncertainty
    "Active": 1.0,  # baseline
    "Seasonal": 1.8,  # peak/offpeak mismatch
    "Phasing Out": 1.4,
    "Discontinued": 1.3,  # supply cut
}
# LIFECYCLE_STOCKOUT_MULTIPLIER = {
#     "New": lambda t: 1.2 + 0.5 * exp(-t/30),
#     "Active": lambda t: 1.0,
#     "Seasonal": lambda t: 1.2 + seasonal_spike_factor,
#     "Discontinued": lambda t: 1.1,
# }


STORE_STOCKOUT_MULTIPLIER = {
    "Flagship": 0.9,  # needs large buffer stock
    "Mall": 1.0,  # predictable footfall
    "Neighbourhood": 1.2,  # small storage, daily spikes
    "Online": 1.3,  # promotion driven surge, long tail products
}


STOCKOUT_DURATION_BY_STATUS = {
    "New": (1, 10),  # volatile launch + forecast errors
    "Active": (2, 10),  # stable supply chain (tightened upper bound)
    "Seasonal": (3, 45),  # demand spikes + stock planning lag
    "Phasing Out": (2, 25),
    "Discontinued": (
        10,
        120,
    ),  # leftover demand + slow clearance + missing replenishment
}


STOCKOUT_DURATION_BY_CATEGORY = {
    # Ultra-perishable
    "Fresh Produce": (1, 3),
    "Bakery": (1, 2),
    "Meat & Seafood": (1, 3),
    # Cold chain
    "Dairy & Eggs": (1, 4),
    "Frozen Food": (2, 7),
    # High-volume FMCG
    "Snacks": (2, 6),
    "Beverages": (2, 5),
    "Breakfast Foods": (2, 6),
    # Shelf-stable
    "Pantry Staples": (3, 10),
    "Rice & Noodles": (4, 14),
    "Canned Goods": (4, 14),
    # Non-food essentials
    "Household Essentials": (3, 10),
    "Cleaning Supplies": (3, 12),
    "Personal Care": (4, 12),
    "Health & Beauty": (4, 14),
    "Baby Products": (4, 14),
    # Long lead time
    "Electronics & Appliances": (7, 30),
    "Home & Living": (7, 21),
    "Sports, Travel & Leisure": (5, 21),
}


STOCKOUT_AMOUNT_OF_TIMES_BY_CATEGORY = {
    "Fresh Produce": (6, 20),
    "Meat & Seafood": (6, 18),
    "Bakery": (8, 24),
    "Dairy & Eggs": (3, 10),
    "Frozen Food": (2, 6),
    "Snacks": (2, 8),
    "Beverages": (2, 8),
    "Breakfast Foods": (2, 6),
    "Pantry Staples": (1, 4),
    "Rice & Noodles": (1, 3),
    "Canned Goods": (1, 3),
    "Household Essentials": (1, 4),
    "Cleaning Supplies": (1, 4),
    "Personal Care": (1, 4),
    "Health & Beauty": (1, 4),
    "Baby Products": (1, 4),
    "Electronics & Appliances": (0, 2),
    "Home & Living": (0, 2),
    "Sports, Travel & Leisure": (0, 3),
}


BRAND_STOCKOUT_NUM_OF_TIMES_MULTIPLIER = {
    # FMCG giants – extremely stable
    "Coca-Cola": 0.6,
    "Pepsi": 0.65,
    "Nestle": 0.65,
    "Kellogg's": 0.7,
    "Unilever": 0.7,
    # Strong regional brands
    "Lays": 0.75,
    "Pringles": 0.75,
    "Oreo": 0.8,
    "Meiji": 0.8,
    "Marigold": 0.85,
    # Mid-tier / regional suppliers
    "Ayam Brand": 1.0,
    "San Remo": 1.0,
    "Gardenia": 1.1,
    "Sunshine": 1.1,
    # Fresh / fragmented suppliers
    "Zenxin Organic Food": 1.4,
    "Little Farms": 1.45,
    # Electronics / import-heavy
    "Dyson": 1.3,
    "Xiaomi": 1.15,
    "Samsung": 1.1,
}


CATEGORY_BASE_STOCK = {
    "Snacks": (40, 80),
    "Beverages": (50, 100),
    "Dairy & Eggs": (20, 50),
    "Frozen Food": (30, 60),
    "Fresh Produce": (10, 30),
    "Pantry Staples": (50, 100),
    "Household Essentials": (30, 70),
    "Health & Beauty": (10, 30),
    "Baby Products": (10, 30),
    "Canned Goods": (40, 80),
    "Personal Care": (20, 50),
    "Meat & Seafood": (10, 25),
    "Bakery": (15, 40),
    "Cleaning Supplies": (20, 50),
    "Rice & Noodles": (50, 100),
    "Breakfast Foods": (30, 70),
    "Electronics & Appliances": (5, 20),
    "Home & Living": (10, 30),
    "Sports, Travel & Leisure": (10, 30),
}


STOCK_BANDS = {
    "0": (0, 0),
    "1-5": (1, 5),
    "6-20": (6, 20),
    "21-100": (21, 100),
    "101+": (101, 10000000),
}

STOCK_STATUSES = {
    "0": "Out of Stock",
    "1-5": "Limited Stock",
    "6-20": "Low Stock",
    "21-100": "In Stock",
    "101+": "Overstocked",
}

IN_STOCK_STATUS = [
    "Limited Stock",
    "Low Stock",
    "In Stock",
]


EVENT_STOCK_DROP_RATES = {
    "Black Friday": (0.4, 0.65),
    "1111": (0.15, 0.35),
    "1212": (0.2, 0.4),
    "Chinese New Year": (0.1, 0.3),
    "Hari Raya Puasa": (0.35, 0.6),
    "Diwali": (0.3, 0.55),
    "Christmas": (0.25, 0.5),
}


STORE_OVERORDER_BIAS = {
    "Mall": 0.25,
    "Flagship": 0.15,
    "Neighbourhood": 0.05,
    "Online": 0.10,
}
