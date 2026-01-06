import random
from datetime import date

import pandas as pd
from config import (
    GLOBAL_DESCRIPTORS,
    NEGATIVE_ADJECTIVES,
    NEGATIVE_CATEGORY_DESCRIPTORS,
    NEGATIVE_DESCRIPTOR_TEMPLATES,
    NEGATIVE_VERBS,
    NEUTRAL_CATEGORY_DESCRIPTORS,
    NEUTRAL_PHRASES,
    NEUTRAL_VERBS,
    NUM_REVIEWS,
    POSITIVE_ADJECTIVES,
    POSITIVE_CATEGORY_DESCRIPTORS,
    POSITIVE_DESCRIPTOR_TEMPLATES,
    POSITIVE_VERBS,
)
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

reviews = []
review_ids = []

def generate_mention_text(mention_type, product_name, value, sentiment, price=None):
    if sentiment == "positive" or sentiment == "neutral":
        if mention_type in POSITIVE_DESCRIPTOR_TEMPLATES and value is not None:
            template = random.choice(POSITIVE_DESCRIPTOR_TEMPLATES[mention_type])
            return template.replace("${value}", str(value)).replace(
                "${product}", product_name
            )
    elif sentiment == "negative":
        if mention_type in NEGATIVE_DESCRIPTOR_TEMPLATES and value is not None:
            template = random.choice(NEGATIVE_DESCRIPTOR_TEMPLATES[mention_type])
            return template.replace("${value}", str(value)).replace(
                "${product}", product_name
            )
    return ""

products_df = pd.read_csv("data_generation/raw_data/products_raw.csv")
product_ids = products_df["product_id"].dropna().tolist()

customers_df = pd.read_csv("data_generation/raw_data/customers_raw.csv")
customer_ids = customers_df["customer_id"].dropna().tolist()

for i in range(1, NUM_REVIEWS + 1):
    rid = f"REV{i:03d}"
    review_ids.append(rid)

    customer_id = random.choice(customer_ids)
    product_id = random.choice(product_ids)
    product_row = products_df[products_df["product_id"] == product_id]
    product_name = product_row["product_name"].iloc[0]
    category = product_row["category"].iloc[0]
    selling_price = product_row["selling_price"].iloc[0]
    sentiment = random.choices(["positive", "neutral", "negative"], weights=[0.6, 0.2, 0.2])[0]

    if sentiment == "negative":
        descriptors_pool = NEGATIVE_CATEGORY_DESCRIPTORS.get(category, {}).copy()
    elif sentiment == "positive":
        descriptors_pool = POSITIVE_CATEGORY_DESCRIPTORS.get(category, {}).copy()
    elif sentiment == "neutral":
        descriptors_pool = NEUTRAL_CATEGORY_DESCRIPTORS.get(category, {}).copy()

    descriptor_values = {}
    for d_type, options in descriptors_pool.items():
        if options:
            descriptor_values[d_type] = random.choice(options)

    for special in ["packaging", "promotion"]:
        if special not in descriptor_values or random.random() < 0.3:
            descriptor_values[special] = random.choice(
                GLOBAL_DESCRIPTORS[special].get(
                    sentiment, GLOBAL_DESCRIPTORS[special]["neutral"]
                )
            )

    mention_types = random.sample(
        list(descriptor_values.keys()), k=min(2, len(descriptor_values))
    )
    sentences = []

    for mention_type in mention_types:
        value = descriptor_values.get(mention_type)
        sentence = generate_mention_text(
            mention_type, product_name, value, sentiment, selling_price
        )
        if sentence:
            sentences.append(sentence)

    mention_text = " ".join(sentences)

    positive_templates = [
        f"{random.choice(POSITIVE_VERBS).capitalize()} this product! It's {random.choice(POSITIVE_ADJECTIVES)}.{mention_text}",
        f"This product is {random.choice(POSITIVE_ADJECTIVES)} and I {random.choice(POSITIVE_VERBS)} it.{mention_text}",
        f"Absolutely {random.choice(POSITIVE_ADJECTIVES)}! {random.choice(POSITIVE_VERBS).capitalize()} it.{mention_text}",
        f"I {random.choice(POSITIVE_VERBS)} {product_name}. Truly {random.choice(POSITIVE_ADJECTIVES)}.{mention_text}",
        f"{product_name} exceeded my expectations. {random.choice(POSITIVE_VERBS).capitalize()} it!{mention_text}",
        f"I've been using {product_name} for a while and it's {random.choice(POSITIVE_ADJECTIVES)}.{mention_text}",
        f"{random.choice(POSITIVE_VERBS).capitalize()} this! {product_name} is {random.choice(POSITIVE_ADJECTIVES)}.",
        f"Highly {random.choice(['recommended', 'suggested', 'endorsed'])}! {product_name} is {random.choice(POSITIVE_ADJECTIVES)}.{mention_text}",
        f"Can't get enough of {product_name}! It's {random.choice(POSITIVE_ADJECTIVES)}.{mention_text}",
        f"One of the best purchases I've made this year! {product_name} is {random.choice(POSITIVE_ADJECTIVES)}.{mention_text}",
        f"{product_name} really impressed me. {random.choice(POSITIVE_VERBS).capitalize()} it!{mention_text}",
    ]

    neutral_templates = [
        f"This product is {random.choice(NEUTRAL_PHRASES)}.{mention_text}",
        f"I {random.choice(NEUTRAL_VERBS)} {product_name} to be {random.choice(NEUTRAL_PHRASES)}.{mention_text}",
        f"{product_name} is {random.choice(NEUTRAL_PHRASES)}, nothing fancy.{mention_text}",
        f"Overall, {product_name} seems {random.choice(NEUTRAL_PHRASES)}.{mention_text}",
        f"{product_name} is okay. {random.choice(['Nothing special', 'Meets expectations', 'Average quality'])}.{mention_text}",
        f"Using {product_name} was {random.choice(NEUTRAL_PHRASES)}. Would buy again? Not sure.{mention_text}",
        f"Just tried {product_name}. It's {random.choice(NEUTRAL_PHRASES)}.{mention_text}",
        f"{product_name} serves its purpose. {random.choice(NEUTRAL_PHRASES).capitalize()} quality.{mention_text}",
        f"Nothing extraordinary about {product_name}. It's {random.choice(NEUTRAL_PHRASES)}.{mention_text}",
        f"{product_name} is acceptable for the price.{mention_text}",
    ]

    negative_templates = [
        f"{random.choice(NEGATIVE_VERBS).capitalize()} {product_name}. It's {random.choice(NEGATIVE_ADJECTIVES)}.{mention_text}",
        f"I {random.choice(NEGATIVE_VERBS)} this product. {product_name} felt {random.choice(NEGATIVE_ADJECTIVES)}.{mention_text}",
        f"Unfortunately, {product_name} is {random.choice(NEGATIVE_ADJECTIVES)}. {random.choice(NEGATIVE_VERBS).capitalize()} it.{mention_text}",
        f"{product_name} did not meet my expectations. {random.choice(NEGATIVE_VERBS).capitalize()} it.{mention_text}",
        f"Really {random.choice(NEGATIVE_ADJECTIVES)} experience with {product_name}.{mention_text}",
        f"{product_name} disappointed me. {random.choice(NEGATIVE_VERBS).capitalize()} it!{mention_text}",
        f"Not impressed with {product_name}. It's {random.choice(NEGATIVE_ADJECTIVES)}.{mention_text}",
        f"{product_name} didn't live up to the hype. {random.choice(NEGATIVE_VERBS).capitalize()} this product.{mention_text}",
        f"{random.choice(NEGATIVE_ADJECTIVES).capitalize()} quality. I {random.choice(NEGATIVE_VERBS)} {product_name}.{mention_text}",
        f"{product_name} is subpar. {random.choice(NEGATIVE_VERBS).capitalize()} it.{mention_text}",
        f"Very {random.choice(NEGATIVE_ADJECTIVES)}! {product_name} is disappointing.{mention_text}",
    ]

    if sentiment == "positive":
        review_text = random.choice(positive_templates)
        rating = random.randint(4, 5)
    elif sentiment == "neutral":
        review_text = random.choice(neutral_templates)
        rating = 3
    else:
        review_text = random.choice(negative_templates)
        rating = random.randint(1, 2)

    texting_shorthand = {
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

    if random.random() < 0.25:
        for word, short in texting_shorthand.items():
            if random.random() < 0.5:
                review_text = review_text.replace(word, short)

    if random.random() < 0.3:
        review_text = review_text.lower()

    review = {
        "review_id": rid,
        "product_id": product_id,
        "customer_id": customer_id,
        "rating": rating,
        "review_text": review_text,
        "review_date": fake.date_between(start_date=date(2024,1,1), end_date=date(2024,12,31))
    }

    reviews.append(review)

df_reviews = pd.DataFrame(reviews)
df_reviews.to_csv("data_generation/raw_data/product_reviews.csv", index=False)
print("product_reviews_raw.csv file generated")
