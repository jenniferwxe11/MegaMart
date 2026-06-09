from datetime import date, datetime

import pandas as pd

DATA_START_DATE = pd.Timestamp("2023-01-01")
DATA_END_DATE = pd.Timestamp("2025-12-31")
SIMULATION_DATE = pd.Timestamp("2025-12-31")
RAW_DIR = "data_generation/raw_data"

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


REGIONS_TO_AREAS: dict[str, list[str]] = {
    "Central": [
        "Orchard",
        "Somerset",
        "Dhoby Ghaut",
        "City Hall",
        "Raffles Place",
        "Marina Bay",
        "Marina South",
        "Tanjong Pagar",
        "Outram",
        "Chinatown",
        "Clarke Quay",
        "River Valley",
        "Newton",
        "Novena",
        "Toa Payoh",
        "Bishan",
        "Bugis",
        "Rochor",
        "Little India",
        "Farrer Park",
        "Tiong Bahru",
        "Queenstown",
        "Redhill",
        "Alexandra",
        "Bukit Timah",
        "Upper Bukit Timah",
        "Holland Village",
        "Tanglin",
        "Marine Parade",
        "Kallang",
        "Geylang",
    ],
    "North": [
        "Yishun",
        "Khatib",
        "Sembawang",
        "Canberra",
        "Woodlands",
        "Admiralty",
        "Mandai",
        "Sungei Kadut",
    ],
    "North-East": [
        "Ang Mo Kio",
        "Serangoon",
        "Lorong Chuan",
        "Kovan",
        "Hougang",
        "Buangkok",
        "Sengkang",
        "Compassvale",
        "Rivervale",
        "Punggol",
        "Woodleigh",
    ],
    "East": [
        "Bedok",
        "Kembangan",
        "Eunos",
        "Paya Lebar",
        "Simei",
        "Tanah Merah",
        "Changi",
        "Expo",
        "Tampines",
        "Tampines East",
        "Tampines West",
        "Pasir Ris",
        "Loyang",
    ],
    "West": [
        "Bukit Batok",
        "Bukit Gombak",
        "Bukit Panjang",
        "Choa Chu Kang",
        "Yew Tee",
        "Clementi",
        "Dover",
        "Jurong East",
        "Jurong West",
        "Pioneer",
        "Boon Lay",
        "Lakeside",
        "Chinese Garden",
        "West Coast",
        "Tuas",
        "Tengah",
    ],
}
