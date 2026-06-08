from typing import TypedDict


class PersonaConfig(TypedDict):
    weight: float
    sentence_count: tuple[int, int]
    style: str


REVIEWER_PERSONAS: dict[str, PersonaConfig] = {
    "minimalist": {
        "weight": 0.35,
        "sentence_count": (1, 2),
        "style": "short",
    },
    "balanced": {
        "weight": 0.40,
        "sentence_count": (2, 4),
        "style": "normal",
    },
    "detailed": {
        "weight": 0.25,
        "sentence_count": (4, 7),
        "style": "long",
    },
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
        "At ${value}, I think it's worth every cent.",
        "For ${value}, this is genuinely good value.",
        "${value} feels like a fair price for what you get.",
        "Price-wise, ${value} seems fair for what you get.",
        "For ${value}, this is a good deal.",
        "Considering the quality, ${value} is very reasonable.",
        "${value} feels like a worthwhile investment.",
        "The cost of ${value} is justified by its performance.",
        "Would pay ${value} again without hesitation.",
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
        "Not worth the ${value} price tag at all.",
        "At ${value}, not worth it.",
        "For ${value}, I expected much better.",
        "Overpriced at ${value} for what it delivers.",
        "${value} is too much to pay for this quality.",
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


TEXTING_SHORTHAND = {
    "you": "u",
    "are": "r",
    "please": "pls",
    "people": "ppl",
    "message": "msg",
    "before": "b4",
    "with": "w",
    "really": "rly",
    "thanks": "thx",
    "okay": "ok",
    "see": "c",
    "about": "abt",
    "today": "tdy",
    "very": "v",
    "great": "gr8",
    "love": "luv",
}


CONTEXTUAL_OPENERS = {
    "positive": [
        "Bought this for the family and everyone loved it.",
        "Was skeptical at first but pleasantly surprised.",
        "Reordering this for the third time.",
        "Saw it on promotion and decided to try — no regrets.",
        "My go-to now.",
        "A friend recommended this and they were right.",
    ],
    "neutral": [
        "Tried this out of curiosity.",
        "Picked this up when my usual brand was out of stock.",
        "It was on sale so I gave it a shot.",
        "Not my first choice but it was available.",
    ],
    "negative": [
        "Really disappointed with this purchase.",
        "Won't be buying this again.",
        "Expected better based on the product description.",
        "Had high hopes but they were let down.",
        "Bought as a replacement for my usual brand — big mistake.",
        "Arrived and immediately noticed something was off.",
    ],
}


CONTEXTUAL_CLOSERS = {
    "positive": [
        "Would definitely recommend.",
        "Will buy again.",
        "Solid product overall.",
        "Great value for money.",
        "5 stars, no hesitation.",
    ],
    "neutral": [
        "Might try again, might not.",
        "Would only repurchase if on sale.",
        "Does the job, nothing more.",
        "Acceptable for the price.",
    ],
    "negative": [
        "Save your money.",
        "Would not recommend.",
        "Going back to my old brand.",
        "Gave it 2 chances — still bad.",
        "Avoid.",
    ],
}


NEGATIVE_FAILURE_SNIPPETS = {
    "Fresh Produce": [
        "Half the items were already going soft when they arrived.",
        "Wilted within a day of delivery.",
        "Not as fresh as what I'd get in store.",
    ],
    "Bakery": [
        "Was stale right out of the packaging.",
        "Expiry date was only 2 days away when it arrived.",
    ],
    "Meat & Seafood": [
        "Smelled off when I opened the package.",
        "The portions were much smaller than shown in the photo.",
    ],
    "Electronics & Appliances": [
        "Stopped working after 2 weeks.",
        "The build feels really plasticky in person.",
        "Had connectivity issues from day one.",
    ],
    "Health & Beauty": [
        "Caused skin irritation after a few uses.",
        "The pump broke after the second use.",
    ],
    "Dairy & Eggs": [
        "One of the eggs was cracked on arrival.",
        "The yoghurt was already partially separated.",
    ],
}


TYPO_POOL = {
    "the": ["teh", "th", "the"],
    "and": ["adn", "nd"],
    "good": ["goood", "goof"],
    "great": ["graet", "greta"],
    "product": ["prodcut", "prdouct"],
    "quality": ["quailty", "qualiy"],
    "would": ["woud", "wuold"],
}


FILLERS = {
    "positive": ["Honestly,", "Surprisingly,", "To be fair,", "Not gonna lie,"],
    "neutral": ["To be honest,", "I mean,", "Honestly,"],
    "negative": ["Unfortunately,", "Sadly,", "To be honest,"],
}


SENTIMENT_TEMPLATES = {
    "positive": [
        "Really loved this one — {product_name} is just {adj}.",
        "{product_name} exceeded my expectations. {verb} it!",
        "Honestly can't get enough of {product_name}. It's {adj}.",
        "One of the better purchases I've made recently. {product_name} is {adj}.",
        "Highly recommended — {product_name} is {adj} and worth it.",
    ],
    "neutral": [
        "{product_name} is {phrase}, nothing fancy.",
        "Overall, {product_name} seems {phrase}. Does what it says.",
        "Using {product_name} was {phrase}. Would buy again? Not sure.",
        "{product_name} serves its purpose. {phrase} quality.",
        "Nothing extraordinary, but {product_name} is {phrase} for the price.",
    ],
    "negative": [
        "{product_name} didn't live up to the hype. {adj} experience.",
        "Really {adj} — {product_name} disappointed me.",
        "{product_name} did not meet my expectations at all. {adj}.",
        "{verb} this product. {product_name} felt {adj}.",
        "Unfortunately, {product_name} is {adj}. Would not recommend.",
    ],
}


PRICE_SENSITIVE_CATEGORIES = {
    "Electronics & Appliances",
    "Health & Beauty",
    "Sports, Travel & Leisure",
    "Home & Living",
    "Baby Products",
    "Personal Care",
}
