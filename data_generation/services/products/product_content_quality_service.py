import random

from faker import Faker

fake = Faker()
# ------------------------------
# Helper Functions
# ------------------------------


def generate_content_characteristics(quality_tier, total_attributes):
    """
    Assigns content characteristics based on quality tier.

    Business interpretation:
    - Poor: minimal content
    - Average: acceptable baseline
    - Good: strong merchandising quality
    - Excellent: fully optimized product detail page
    """
    if quality_tier == "Poor":
        image_count = random.choices([0, 1], weights=[0.6, 0.4], k=1)[0]
        image_quality_score = round(random.uniform(0.1, 0.4), 2)
        has_nutritional_info = random.random() < 0.3
        has_description = random.random() < 0.5
        description_length = random.randint(10, 50) if has_description else 0
        missing_attribute_count = random.randint(
            int(0.5 * total_attributes), total_attributes
        )

    elif quality_tier == "Average":
        image_count = random.randint(1, 3)
        image_quality_score = round(random.uniform(0.4, 0.7), 2)
        has_nutritional_info = random.random() < 0.6
        has_description = True
        description_length = random.randint(50, 120)
        missing_attribute_count = random.randint(
            int(0.2 * total_attributes), int(0.5 * total_attributes)
        )

    elif quality_tier == "Good":
        image_count = random.randint(3, 5)
        image_quality_score = round(random.uniform(0.7, 0.9), 2)
        has_nutritional_info = random.random() < 0.8
        has_description = True
        description_length = random.randint(120, 250)
        missing_attribute_count = random.randint(0, int(0.2 * total_attributes))

    else:  # Excellent
        image_count = random.randint(5, 8)
        image_quality_score = round(random.uniform(0.9, 1.0), 2)
        has_nutritional_info = True
        has_description = True
        description_length = random.randint(250, 500)
        missing_attribute_count = 0

    has_image = image_count > 0

    content = {
        "image_count": image_count,
        "has_image": has_image,
        "image_quality_score": image_quality_score,
        "has_nutritional_info": has_nutritional_info,
        "has_description": has_description,
        "description_length": description_length,
        "missing_attribute_count": missing_attribute_count,
    }

    return content
