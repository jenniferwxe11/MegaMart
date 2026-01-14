import random
from datetime import timedelta

import pandas as pd
from config import (
    CATEGORY_CAMPAIGN_PROBABILITY,
    CATEGORY_CODE_MAP,
    NUM_CAMPAIGNS,
    SEASON_CODE_MAP,
    SEASON_PEAK_CATEGORIES,
    SEASONAL_DATES,
    SEGMENT_CATEGORY_BIAS,
    TARGET_SEGMENT,
)
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

adjectives = ["Mega", "Hot", "Exclusive", "Limited-Time", "Weekly", "Flash", "VIP"]
campaign_name_suffixes = ["Sale", "Deals", "Offer", "Promotions"]


def generate_discount_code(discount_type, category=None, season=None):
    discount = random.randint(5, 30)

    if discount_type == "Discount on Category":
        if season and category:
            prefix = SEASON_CODE_MAP.get(
                season, season.upper()
            ) + CATEGORY_CODE_MAP.get(
                category, "".join(word[0] for word in category.split()).upper()
            )
            return discount, f"{prefix}{discount}"
        elif season:
            prefix = SEASON_CODE_MAP.get(season, season.upper())
            return discount, f"{prefix}{discount}"
        elif category:
            prefix = CATEGORY_CODE_MAP.get(
                category, "".join(word[0] for word in category.split()).upper()
            )
            return discount, f"{prefix}{discount}"
        else:
            prefix = "ALL"
            return discount, f"{prefix}{discount}"

    if discount_type == "Discount on Cart":
        if season:
            prefix = SEASON_CODE_MAP.get(season, season.upper())
            return discount, f"{prefix}SAVE{discount}"
        else:
            prefix = random.choice(["SAVE", "DEAL", "MEGA", "PROMO", "OFFER"])
            return discount, f"{prefix}{discount}"


def assign_offer_type(campaign_type, target_segment, season=None, category=None):

    if campaign_type == "seasonal":
        # baseline: discount on 3-6 categories
        if category:
            discount, discount_code = generate_discount_code(
                "Discount on Category", category=category, season=season
            )
            return {
                "offer_type": "Discount on Category",
                "discount_percentage": discount,
                "discount_code": discount_code,
                "free_shipping": False,
            }

        # segment level bonus
        else:
            if target_segment in [
                "New Customers",
                "Churn Risk Customers",
                "Budget Shoppers",
            ]:
                return {
                    "offer_type": "Free Shipping",
                    "discount_percentage": None,
                    "discount_code": "FREESHIPPING",
                    "free_shipping": True,
                }
            else:
                discount, discount_code = generate_discount_code(
                    "Discount on Cart", season=season
                )
                return {
                    "offer_type": "Discount on Cart",
                    "discount_percentage": discount,
                    "discount_code": discount_code,
                    "free_shipping": False,
                }

    elif campaign_type == "category":
        discount, discount_code = generate_discount_code(
            "Discount on Category", category=category
        )
        return {
            "offer_type": "Discount on Category",
            "discount_percentage": discount,
            "discount_code": discount_code,
            "free_shipping": False,
        }

    else:  # generic
        if target_segment in [
            "New Customers",
            "Churn Risk Customers",
            "Budget Shoppers",
        ]:
            return {
                "offer_type": "Free Shipping",
                "discount_percentage": None,
                "discount_code": "FREESHIPPING",
                "free_shipping": True,
            }
        else:
            choice = random.choice(["Discount on Cart", "Free Shipping"])
            if choice == "Free Shipping":
                return {
                    "offer_type": "Free Shipping",
                    "discount_percentage": None,
                    "discount_code": "FREESHIPPING",
                    "free_shipping": True,
                }
            else:
                discount, discount_code = generate_discount_code("Discount on Cart")
                return {
                    "offer_type": "Discount on Cart",
                    "discount_percentage": discount,
                    "discount_code": discount_code,
                    "free_shipping": False,
                }


def generate_campaigns(num_of_campaigns):
    campaigns = []
    campaign_ids = []
    i = 1

    # seasonal campaigns
    for season, (start, end) in SEASONAL_DATES.items():
        categories = SEASON_PEAK_CATEGORIES.get(season, [])
        stacked_categories = random.sample(
            categories, random.randint(3, min(6, len(categories)))
        )
        for stacked_category in stacked_categories:
            last_word = random.choice(campaign_name_suffixes)
            for segment in list(TARGET_SEGMENT.keys()):
                campaign_id = f"CAMP{i:03d}"
                name = f"MegaMart {season} {stacked_category} {last_word}"
                offer = assign_offer_type(
                    campaign_type="seasonal",
                    target_segment=segment,
                    season=season,
                    category=stacked_category,
                )
                budget = int(round(random.randint(500, 50000) / 100)) * 100
                base = min(budget / 50000, 1.0)
                kpi_conversion_uplift_target = round(
                    0.02 + base * random.uniform(0.03, 0.15), 3
                )
                kpi_revenue_uplift_target = round(
                    0.03 + base * random.uniform(0.05, 0.25), 3
                )
                kpi_engagement_target = round(
                    0.05 + base * random.uniform(0.10, 0.35), 3
                )
                is_ab_test = False
                if random.random() < 0.8:
                    is_ab_test = True
                campaign_ids.append(campaign_id)
                campaigns.append(
                    {
                        "campaign_id": campaign_id,
                        "name": name,
                        "campaign_type": "seasonal",
                        "target_segment": segment,
                        "category": stacked_category,
                        "channel": random.choice(
                            ["Email", "Push Notifications", "SMS"]
                        ),
                        "offer_type": offer["offer_type"],
                        "discount_percentage": offer["discount_percentage"],
                        "discount_code": offer["discount_code"],
                        "free_shipping": offer["free_shipping"],
                        "start_date": start,
                        "end_date": end,
                        "budget": budget,
                        "is_ab_test": is_ab_test,
                        "kpi_conversion_uplift_target": kpi_conversion_uplift_target,
                        "kpi_revenue_uplift_target": kpi_revenue_uplift_target,
                        "kpi_engagement_target": kpi_engagement_target,
                    }
                )
                i += 1

        for segment in ["New Customers", "Churn Risk Customers", "Budget Shoppers"]:
            campaign_id = f"CAMP{i:03d}"
            name = f"MegaMart {season} {random.choice(campaign_name_suffixes)}"
            offer = assign_offer_type(
                campaign_type="seasonal", target_segment=segment, season=season
            )
            budget = int(round(random.randint(500, 50000) / 100)) * 100
            base = min(budget / 50000, 1.0)
            kpi_conversion_uplift_target = round(
                0.02 + base * random.uniform(0.03, 0.15), 3
            )
            kpi_revenue_uplift_target = round(
                0.03 + base * random.uniform(0.05, 0.25), 3
            )
            kpi_engagement_target = round(0.05 + base * random.uniform(0.10, 0.35), 3)
            is_ab_test = False
            if random.random() < 0.8:
                is_ab_test = True
            campaign_ids.append(campaign_id)
            campaigns.append(
                {
                    "campaign_id": campaign_id,
                    "name": name,
                    "campaign_type": "seasonal",
                    "target_segment": segment,
                    "category": None,
                    "channel": random.choice(["Email", "Push Notifications", "SMS"]),
                    "offer_type": offer["offer_type"],
                    "discount_percentage": offer["discount_percentage"],
                    "discount_code": offer["discount_code"],
                    "free_shipping": offer["free_shipping"],
                    "start_date": start,
                    "end_date": end,
                    "budget": budget,
                    "is_ab_test": is_ab_test,
                    "kpi_conversion_uplift_target": kpi_conversion_uplift_target,
                    "kpi_revenue_uplift_target": kpi_revenue_uplift_target,
                    "kpi_engagement_target": kpi_engagement_target,
                }
            )
            i += 1

        for segment in ["Active Customers", "High Spenders"]:
            campaign_id = f"CAMP{i:03d}"
            name = f"MegaMart {season} {random.choice(campaign_name_suffixes)}"
            offer = assign_offer_type(
                campaign_type="seasonal", target_segment=segment, season=season
            )
            budget = int(round(random.randint(500, 50000) / 100)) * 100
            base = min(budget / 50000, 1.0)
            kpi_conversion_uplift_target = round(
                0.02 + base * random.uniform(0.03, 0.15), 3
            )
            kpi_revenue_uplift_target = round(
                0.03 + base * random.uniform(0.05, 0.25), 3
            )
            kpi_engagement_target = round(0.05 + base * random.uniform(0.10, 0.35), 3)
            is_ab_test = False
            if random.random() < 0.8:
                is_ab_test = True
            campaign_ids.append(campaign_id)
            campaigns.append(
                {
                    "campaign_id": campaign_id,
                    "name": name,
                    "campaign_type": "seasonal",
                    "target_segment": segment,
                    "category": None,
                    "channel": random.choice(["Email", "Push Notifications", "SMS"]),
                    "offer_type": offer["offer_type"],
                    "discount_percentage": offer["discount_percentage"],
                    "discount_code": offer["discount_code"],
                    "free_shipping": offer["free_shipping"],
                    "start_date": start,
                    "end_date": end,
                    "budget": budget,
                    "is_ab_test": is_ab_test,
                    "kpi_conversion_uplift_target": kpi_conversion_uplift_target,
                    "kpi_revenue_uplift_target": kpi_revenue_uplift_target,
                    "kpi_engagement_target": kpi_engagement_target,
                }
            )
            i += 1

    # generic and category campaigns
    while i <= num_of_campaigns:
        category = None
        target_segment = None
        campaign_type = random.choices(
            ["generic", "category"],
            weights=[0.4, 0.6],
            k=1,
        )[0]
        if campaign_type == "generic":
            name = f"MegaMart {random.choice(adjectives)} {random.choice(campaign_name_suffixes)}"
            target_segment = random.choices(
                list(TARGET_SEGMENT.keys()),
                weights=list(TARGET_SEGMENT.values()),
                k=1,
            )[0]
        else:  # category
            category = random.choices(
                list(CATEGORY_CAMPAIGN_PROBABILITY.keys()),
                weights=list(CATEGORY_CAMPAIGN_PROBABILITY.values()),
                k=1,
            )[0]
            name = f"MegaMart {category} {random.choice(campaign_name_suffixes)}"
            # bias target segment based on category, excludes churn risk customers
            possible_segments = []
            for segment, biased_categories in SEGMENT_CATEGORY_BIAS.items():
                if biased_categories == "All" or category in biased_categories:
                    possible_segments.append(segment)
            if possible_segments:
                target_segment = random.choice(possible_segments)
            else:
                target_segment = random.choices(list(SEGMENT_CATEGORY_BIAS.keys()))[0]

        campaign_id = f"CAMP{i:03d}"
        offer = assign_offer_type(campaign_type, segment, category)
        start = fake.date_between(start_date="-12M", end_date="-1M")
        end = start + timedelta(weeks=1)
        budget = int(round(random.randint(500, 50000) / 100)) * 100
        base = min(budget / 50000, 1.0)
        is_ab_test = random.random() < 0.8
        kpi_conversion_uplift_target = round(
            0.02 + base * random.uniform(0.03, 0.15), 3
        )
        kpi_revenue_uplift_target = round(0.03 + base * random.uniform(0.05, 0.25), 3)
        kpi_engagement_target = round(0.05 + base * random.uniform(0.10, 0.35), 3)
        campaign_ids.append(campaign_id)
        campaigns.append(
            {
                "campaign_id": campaign_id,
                "name": name,
                "campaign_type": campaign_type,
                "target_segment": target_segment,
                "category": category,
                "channel": random.choice(["Email", "Push Notifications", "SMS"]),
                "offer_type": offer["offer_type"],
                "discount_percentage": offer["discount_percentage"],
                "discount_code": offer["discount_code"],
                "free_shipping": offer["free_shipping"],
                "start_date": start,
                "end_date": end,
                "budget": budget,
                "is_ab_test": is_ab_test,
                "kpi_conversion_uplift_target": kpi_conversion_uplift_target,
                "kpi_revenue_uplift_target": kpi_revenue_uplift_target,
                "kpi_engagement_target": kpi_engagement_target,
            }
        )
        i += 1
    return campaigns, campaign_ids


campaigns, campaign_ids = generate_campaigns(NUM_CAMPAIGNS)
df_campaigns = pd.DataFrame(campaigns)
df_campaigns.to_csv("data_generation/raw_data/campaigns_raw.csv", index=False)
print("campaigns_raw.csv file generated")
