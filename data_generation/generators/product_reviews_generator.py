import random
from typing import Any

import numpy as np
import pandas as pd

from data_generation.config.generation_config import LIMIT_PRODUCT_REVIEWS
from data_generation.config.product_reviews_config import (
    GLOBAL_DESCRIPTORS,
    NEGATIVE_CATEGORY_DESCRIPTORS,
    NEUTRAL_CATEGORY_DESCRIPTORS,
    POSITIVE_CATEGORY_DESCRIPTORS,
    PRICE_SENSITIVE_CATEGORIES,
    TEXTING_SHORTHAND,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.products.product_review_service import (
    build_review_text,
    generate_mention_text,
    inject_typos,
    sample_persona,
)
from data_generation.utils.io_utils import save


@register("product_reviews_generator")
def product_reviews_generator(ctx: GenerationContext):
    # ---------------------------
    # Load Data
    # ---------------------------

    product_map = ctx.products.product_map

    assert ctx.transactions is not None
    valid_transactions = ctx.transactions.valid_transactions

    # ---------------------------
    # Storage
    # ---------------------------

    reviews: list[dict[str, Any]] = []
    reviewed_pairs = set()

    # ---------------------------
    # Generation
    # ---------------------------

    i = 1

    # Iterate through each completed purchase (1 row = 1 product bought in a transaction)
    for _, transaction_row in valid_transactions.iterrows():
        if len(reviews) >= LIMIT_PRODUCT_REVIEWS:
            break

        # Only ~30% of purchases result in a review
        if random.random() > 0.3:
            continue

        transaction_id = transaction_row["transaction_id"]
        transaction_time = transaction_row["transaction_time"]
        payment_method = transaction_row["payment_method"]

        # Further reduce likelihood for cash payments (~20% chance),
        # reflecting lower engagement with digital review platforms
        if payment_method == "Cash":
            if random.random() > 0.2:
                continue

        review_id = f"REV{i:03d}"

        customer_id = transaction_row["customer_id"]
        product_id = transaction_row["product_id"]
        product_row = product_map.get(product_id)

        if not product_row:
            continue

        product_name = product_row["product_name"]
        category = product_row["category"]
        selling_price = product_row["selling_price"]

        # Avoid duplicate reviews for same purchase
        pair = (customer_id, transaction_id, product_id)
        if pair in reviewed_pairs:
            continue
        reviewed_pairs.add(pair)

        # Sentiment distribution reflects real world skew (more positive reviews)
        sentiment = random.choices(
            ["positive", "neutral", "negative"], weights=[0.6, 0.2, 0.2]
        )[0]

        # Incorporating product/category specific descriptors in the review
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

        # Common attributes (e.g. packaging, promotions) are occasionally mentioned
        for special in ["packaging", "promotion"]:
            if special not in descriptor_values or random.random() < 0.3:
                descriptor_values[special] = random.choice(
                    GLOBAL_DESCRIPTORS[special].get(
                        sentiment, GLOBAL_DESCRIPTORS[special]["neutral"]
                    )
                )

        # Price sensitive categories are more likely to mention price in reviews
        if category in PRICE_SENSITIVE_CATEGORIES and random.random() < 0.35:
            descriptor_values["price"] = str(
                selling_price
            )  # value unused, price param handles it

        # Limit number of attributes mentioned to keep reviews concise and natural
        mention_types = random.sample(
            list(descriptor_values.keys()), k=min(2, len(descriptor_values))
        )

        sentences = []
        for mention_type in mention_types:
            value = descriptor_values.get(mention_type)
            sentence = generate_mention_text(
                mention_type,
                product_name,
                value or "",
                sentiment,
                selling_price,
            )
            if sentence:
                sentences.append(sentence)

        persona = sample_persona()

        review_text = build_review_text(
            sentiment,
            product_name,
            category,
            sentences,
            persona,
        )

        # Casing variation — detailed reviewers write properly, minimalists often do not
        if persona == "minimalist" and random.random() < 0.5:
            review_text = review_text.lower()
        elif persona == "detailed" and random.random() < 0.15:
            review_text = review_text.upper()  # rare all caps ranter

        # Typos — more likely from minimalists
        typo_rate = 0.12 if persona == "minimalist" else 0.04
        if random.random() < 0.3:
            review_text = inject_typos(review_text, typo_rate)

        # Shorthand — minimalists only
        if persona == "minimalist" and random.random() < 0.4:
            for word, short in TEXTING_SHORTHAND.items():
                if random.random() < 0.5:
                    review_text = review_text.replace(word, short)

        # Map sentiment to rating scale
        if sentiment == "positive":
            rating = random.randint(4, 5)
        elif sentiment == "neutral":
            rating = 3
        else:
            rating = random.randint(1, 2)

        # Introduce imperfections in text (shorthand, casing)
        # to mimic real user-generated content
        if random.random() < 0.25:
            for word, short in TEXTING_SHORTHAND.items():
                if random.random() < 0.5:
                    review_text = review_text.replace(word, short)
        if random.random() < 0.3:
            review_text = review_text.lower()

        # Simulate delay between purchase and review submission
        # (most reviews happen within ~2 weeks, skewed towards earlier days)
        delay_days = int(min(np.random.gamma(shape=2, scale=3), 14))
        review_date = transaction_time.date() + pd.Timedelta(days=delay_days)

        # Store Product Review Record
        reviews.append(
            {
                "review_id": review_id,
                "product_id": product_id,
                "customer_id": customer_id,
                "rating": rating,
                "review_text": review_text,
                "review_date": review_date,
            }
        )
        i += 1

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(reviews), "product_reviews_raw.csv")
