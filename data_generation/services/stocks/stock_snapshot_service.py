from datetime import timedelta

import pandas as pd

from data_generation.config.constants import SEASONAL_DATES
from data_generation.config.stocks_config import STOCK_BANDS

# ---------------------------
# Helper Functions
# ---------------------------


def date_range(start_date, end_date, step_days=7):
    """
    Generates a sequence of dates at a fixed interval.
    """
    current = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    while current <= end_date:
        yield current
        current += timedelta(days=step_days)


def get_stock_band(stock_quantity):
    """
    Classifies stock quantity into predefined inventory bands.
    """
    for band, (low, high) in STOCK_BANDS.items():
        if low <= stock_quantity <= high:
            return band
    return "Overstocked"


def get_seasonal_spike():
    """
    Constructs time windows representing seasonal demand periods.

    Effects:
    - Pre-event: increase stock in anticipation of demand
    - During/post-event: reduce stock due to higher sales velocity
    - Mega sales have extended post-event impact vs normal events
    """
    seasonal_spikes = []
    for event_type, events in SEASONAL_DATES.items():
        if event_type == "Commercial Mega Sale":
            for event_name, dates in events.items():
                for date in dates:
                    # Restocking starts 2 weeks before event
                    pre_spike_start = date - timedelta(weeks=2)
                    # Sales end 1 week after event
                    spike_end = date + timedelta(weeks=1)
                    seasonal_spikes.append((pre_spike_start, spike_end, event_name))
        else:
            for event_name, dates in events.items():
                for date in dates:
                    # Restocking starts 2 weeks before event
                    pre_spike_start = date - timedelta(weeks=2)
                    # Sales end on event
                    spike_end = date
                    seasonal_spikes.append((pre_spike_start, spike_end, event_name))
    return seasonal_spikes
