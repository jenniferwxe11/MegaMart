from datetime import datetime, date
import pandas as pd

DATA_START_DATE = pd.Timestamp("2023-01-01")
DATA_END_DATE = pd.Timestamp("2025-12-31")
SIMULATION_DATE = pd.Timestamp("2025-12-31")

SEASONAL_DATES: dict[str, dict[str, list[date]]] = {
    "Commercial Mega Sale": {
        "Black Friday": [
            datetime(2023, 11, 24),
            datetime(2024, 11, 29),
            datetime(2025, 11, 28),
        ],
        "1111": [
            datetime(2023, 11, 11),
            datetime(2024, 11, 11),
            datetime(2025, 11, 11),
        ],
        "1212": [
            datetime(2023, 12, 12),
            datetime(2024, 12, 12),
            datetime(2025, 12, 12),
        ],
    },
    "Cultural Festival": {
        "Chinese New Year": [
            datetime(2023, 1, 22),
            datetime(2024, 2, 10),
            datetime(2025, 1, 29),
        ],
        "Hari Raya Puasa": [
            datetime(2023, 4, 21),
            datetime(2024, 4, 9),
            datetime(2025, 3, 30),
        ],
        "Diwali": [
            datetime(2023, 11, 10),
            datetime(2024, 10, 29),
            datetime(2025, 10, 18),
        ],
        "Christmas": [
            datetime(2023, 12, 25),
            datetime(2024, 12, 25),
            datetime(2025, 12, 25),
        ],
    },
}

RAW_DIR = "data_generation/raw_data"
