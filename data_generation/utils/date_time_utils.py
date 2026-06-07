def overlapping_dates(windows, start, end):
    """
    Checks if a given date range overlaps with any existing windows.
    """
    for s, e in windows:
        if start <= e and end >= s:
            return True
    return False
