# How many enrichment events can happen per product (beyond the initial one)
MAX_ENRICHMENTS = 3
# Minimum and maximum days between enrichment events
ENRICH_GAP = (30, 365)
# Ordered quality tiers
TIERS = ["Poor", "Average", "Good", "Excellent"]

# Probability of advancing to the next tier at each enrichment event
ADVANCE_PROB = {
    "Poor": 0.75,  # Most products escape Poor fairly quickly
    "Average": 0.50,
    "Good": 0.25,  # Excellent is rare — requires dedicated effort
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
