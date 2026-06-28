from datetime import datetime

from data_generation.utils.date_time_utils import (
    get_day_type,
    get_pay_cycle,
    get_seasonal_event,
    get_time_of_day,
)

# ============================================================
# get_day_type()
# ============================================================


def test_clickstream_date_time_utils_get_day_type():
    assert get_day_type(datetime(2024, 1, 6)) == "Weekend"
    assert get_day_type(datetime(2023, 5, 8)) == "Weekday"


# ============================================================
# get_pay_cycle()
# ============================================================


def test_clickstream_date_time_utils_get_pay_cycle():
    assert get_pay_cycle(datetime(2023, 6, 1)) == "Payday"
    assert get_pay_cycle(datetime(2023, 6, 28)) == "Payday Spillover"
    assert get_pay_cycle(datetime(2023, 6, 10)) is None


# ============================================================
# get_seasonal_event()
# ============================================================


def test_clickstream_date_time_utils_get_seasonal_event_commercial_mega_sale_detected():
    season, season_type = get_seasonal_event(datetime(2023, 11, 24))
    assert season == "Black Friday"
    assert season_type == "Commercial Mega Sale"


def test_clickstream_date_time_utils_get_seasonal_event_cultural_festival_detected():
    season, season_type = get_seasonal_event(datetime(2025, 3, 30))
    assert season == "Hari Raya Puasa"
    assert season_type == "Cultural Festival"


def test_clickstream_date_time_utils_get_seasonal_event_no_event_on_random_day():
    season, season_type = get_seasonal_event(datetime(2023, 3, 15))
    assert season is None
    assert season_type is None


# ============================================================
# get_time_of_day()
# ============================================================


def test_clickstream_date_time_utils_get_time_of_day():
    assert get_time_of_day(datetime(2024, 1, 1, 6)) == "Early Morning"
