PRODUCT_LIFECYCLE = {
    "New": 0.05,
    "Active": 0.65,
    "Seasonal": 0.10,
    "Phasing Out": 0.15,
    "Discontinued": 0.05,
}


# Typical dwell time in each status before the next transition (in days)
STATUS_DWELL_DAYS = {
    "New": (14, 120),  # 2 weeks – 4 months
    "Active": (120, 1095),  # 4 months – 3 years (long tail)
    "Seasonal": (60, 180),  # 2–6 months (season-bound)
    "Phasing Out": (30, 180),  # 1–6 months
    "Discontinued": (365, 3650),  # Still exists in history but inactive
}


# Probability that a product progresses to the next status at all
STATUS_TRANSITION_PROB = {
    "New": 0.90,  # Most products survive launch phase
    "Active": 0.20,  # Slow churn into decline
    "Seasonal": 0.80,  # Seasonal products usually exit after season
    "Phasing Out": 0.85,  # Strong likelihood of discontinuation
    "Discontinued": 0.00,  # Terminal state
}


# Status chain
STATUS_CHAIN = {
    "New": ["Active", "Discontinued"],
    "Active": ["Seasonal", "Phasing Out"],
    "Seasonal": ["Active", "Phasing Out"],
    "Phasing Out": ["Discontinued"],
    "Discontinued": [],
}
