import random

from data_generation.config.product_reviews_config import (
    CONTEXTUAL_CLOSERS,
    CONTEXTUAL_OPENERS,
    FILLERS,
    NEGATIVE_ADJECTIVES,
    NEGATIVE_DESCRIPTOR_TEMPLATES,
    NEGATIVE_FAILURE_SNIPPETS,
    NEGATIVE_VERBS,
    NEUTRAL_PHRASES,
    POSITIVE_ADJECTIVES,
    POSITIVE_DESCRIPTOR_TEMPLATES,
    POSITIVE_VERBS,
    REVIEWER_PERSONAS,
    SENTIMENT_TEMPLATES,
    TYPO_POOL,
)

# ---------------------------
# Helper Functions
# ---------------------------


def inject_typos(text: str, typo_rate: float = 0.08) -> str:
    """Randomly introduces realistic typos into review text."""
    words = text.split()
    result = []
    for word in words:
        lower = word.lower().rstrip(".,!")
        if lower in TYPO_POOL and random.random() < typo_rate:
            replacement = random.choice(TYPO_POOL[lower])
            # Preserve trailing punctuation
            punct = word[len(lower) :] if word.lower().startswith(lower) else ""
            result.append(replacement + punct)
        else:
            result.append(word)
    return " ".join(result)


def sample_persona() -> str:
    """Samples a reviewer persona weighted by distribution."""
    personas = list(REVIEWER_PERSONAS.keys())
    weights = [REVIEWER_PERSONAS[p]["weight"] for p in personas]
    return random.choices(personas, weights=weights)[0]


def maybe_add_filler(sentiment: str, persona_style: str) -> str:
    """
    Occasionally adds realistic filler phrases that real reviewers use.
    Keeps reviews from feeling too structured.
    """
    # Only short/normal personas use fillers — detailed reviewers write more formally
    if persona_style in ("short", "normal") and random.random() < 0.2:
        return random.choice(FILLERS.get(sentiment, [])) + " "
    return ""


def build_review_text(
    sentiment: str,
    product_name: str,
    category: str,
    mention_sentences: list,
    persona: str,
) -> str:
    """
    Assembles a review from persona aware building blocks.
    Structure: [filler?] + [opener?] + [mention sentences] + [failure snippet?] + [closer?]
    Persona controls length and whether opener/closer are included.
    """
    parts = []
    style = REVIEWER_PERSONAS[persona]["style"]
    min_s, max_s = REVIEWER_PERSONAS[persona]["sentence_count"]

    # Minimalists skip opener/closer most of the time
    use_opener = random.random() < (0.3 if style == "short" else 0.65)
    use_closer = random.random() < (0.2 if style == "short" else 0.55)

    # Balanced persona: use a template sentence as the anchor
    if style == "normal":
        templates = SENTIMENT_TEMPLATES.get(sentiment, [])
        if templates:
            template = random.choice(templates)
            filled = template.format(
                product_name=product_name,
                adj=random.choice(
                    POSITIVE_ADJECTIVES
                    if sentiment == "positive"
                    else (
                        NEGATIVE_ADJECTIVES
                        if sentiment == "negative"
                        else NEUTRAL_PHRASES
                    )
                ),
                verb=random.choice(
                    POSITIVE_VERBS if sentiment == "positive" else NEGATIVE_VERBS
                ).capitalize(),
                phrase=random.choice(NEUTRAL_PHRASES),
            )
            parts.append(filled)

    # All personas: opener + mention sentences + closer
    else:
        if use_opener:
            filler = maybe_add_filler(sentiment, style)
            opener = random.choice(CONTEXTUAL_OPENERS[sentiment])
            parts.append(filler + opener)

    # Core attribute sentences trimmed to persona budget
    budget = random.randint(min_s, max_s)
    core = mention_sentences[:budget]
    parts.extend(core)

    # Inject a failure snippet for detailed negative reviewers
    if sentiment == "negative" and style in ("normal", "long"):
        snippets = NEGATIVE_FAILURE_SNIPPETS.get(category, [])
        if snippets and random.random() < 0.5:
            parts.append(random.choice(snippets))

    if use_closer:
        parts.append(random.choice(CONTEXTUAL_CLOSERS[sentiment]))

    # Edge case: if nothing was added (e.g. browsing persona with no sentences)
    # fall back to a minimal sentiment statement
    if not parts:
        fallbacks = {
            "positive": f"{product_name} is great.",
            "neutral": f"{product_name} is okay.",
            "negative": f"{product_name} was disappointing.",
        }
        return fallbacks.get(sentiment, f"Tried {product_name}.")

    return " ".join(parts)


def generate_mention_text(
    mention_type: str,
    product_name: str,
    value: str,
    sentiment: str,
    price: float,
) -> str:
    """
    Generates sentiment appropriate sentence fragments describing product attributes.
    Price is injected only for high-consideration categories where reviewers
    naturally comment on value for money.
    """
    # Occasionally inject a price mention for relevant categories
    # Only when mention_type is price and price is provided
    if mention_type == "price" and price is not None:
        formatted_price = f"${price:.2f}"
        if sentiment in ("positive", "neutral"):
            templates = POSITIVE_DESCRIPTOR_TEMPLATES.get("price", [])
        else:
            templates = NEGATIVE_DESCRIPTOR_TEMPLATES.get("price", [])

        if templates:
            template = random.choice(templates)
            return template.replace("${value}", formatted_price).replace(
                "${product}", product_name
            )

    if sentiment in ("positive", "neutral"):
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
