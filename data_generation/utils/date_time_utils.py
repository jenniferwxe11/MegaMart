from data_generation.config.constants import SEASONAL_DATES


def overlapping_dates(windows, start, end):
    """
    Checks if a given date range overlaps with any existing windows.
    """
    for s, e in windows:
        if start <= e and end >= s:
            return True
    return False


def get_time_of_day(timestamp):
    """
    Classifies session timing.

    Returns:
    - "Late Night" for 12am-5am
    - "Early Morning" for 5am-8am
    - "Morning" for 8am-12pm
    - "Afternoon" for 12pm-5pm
    - "Evening" for 5pm-9pm
    - "Night" for 9pm-12am
    """
    if 0 <= timestamp.hour < 5:
        return "Late Night"
    elif 5 <= timestamp.hour < 8:
        return "Early Morning"
    elif 8 <= timestamp.hour < 12:
        return "Morning"
    elif 12 <= timestamp.hour < 17:
        return "Afternoon"
    elif 17 <= timestamp.hour < 21:
        return "Evening"
    elif 21 <= timestamp.hour < 24:
        return "Night"


def get_day_type(timestamp):
    """
    Identifies whether a session occurs on a weekday/weekend.
    """
    if timestamp.weekday() >= 5:
        return "Weekend"
    return "Weekday"


def get_pay_cycle(timestamp):
    """
    Identifies payday related periods.

    Assumption:
    - Payday occurs on 1st and 15th of the month
    - Payday spillover effects occurs around month end/start
    """
    if timestamp.day in [1, 15]:
        return "Payday"
    elif timestamp.day in [28, 29, 30, 31, 1, 2]:
        return "Payday Spillover"
    return None


def get_seasonal_event(timestamp):
    """
    Maps a session to a seasonal event.

    Returns:
    - Commercial Mega Sale (Black Friday, 1111, 1212)
    - Cultural Festival (Chinese New Year, Hari Raya Puasa, Diwali, Christmas)
    """
    for season_type, seasons in SEASONAL_DATES.items():
        for season, date_list in seasons.items():
            for date in date_list:
                if timestamp.date() == date.date():
                    return season, season_type
    return None, None
