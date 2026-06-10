import random

import pandas as pd

from dirty_data_generation.config.constants import MAX_ERRORS_PER_ROW


def coinflip(prob: float) -> bool:
    return random.random() < prob


def _get_errors(df: pd.DataFrame, idx) -> list:
    """
    Safely retrieve error list for a row.
    """
    errors = df.at[idx, "error_types"]

    if isinstance(errors, list):
        return errors.copy()

    return []


def _set_errors(df: pd.DataFrame, idx, errors: list) -> None:
    """
    Safely write error list back.
    """
    df.at[idx, "error_types"] = errors


def _under_cap(errors: list, max_errors: int = MAX_ERRORS_PER_ROW) -> bool:
    """
    Check whether row can receive more errors.
    """
    return len(set(errors)) < max_errors


def append_error(
    df: pd.DataFrame,
    indices,
    error_label: str,
    max_errors: int = MAX_ERRORS_PER_ROW,
) -> None:
    """
    Append an error label to rows by index.
    Deduplicates labels and respects error cap.
    """

    for idx in list(indices):

        errors = _get_errors(df, idx)

        if not _under_cap(errors, max_errors):
            continue

        if error_label not in errors:
            errors.append(error_label)

        _set_errors(df, idx, errors)


def inject_nulls(
    df: pd.DataFrame,
    mask: pd.Series,
    col: str,
    rate: float,
    error_label: str,
    max_errors: int = MAX_ERRORS_PER_ROW,
) -> pd.DataFrame:
    """
    Randomly set values to null.
    """

    eligible = []

    for idx in df.index[mask]:
        errors = _get_errors(df, idx)

        if _under_cap(errors, max_errors):
            eligible.append(idx)

    affected = [idx for idx in eligible if coinflip(rate)]

    if affected:
        df.loc[affected, col] = None
        append_error(
            df,
            affected,
            error_label,
            max_errors=max_errors,
        )

    return df


def inject_whitespace(
    df: pd.DataFrame,
    col: str,
    rate: float,
    error_label: str = "formatting anomaly",
    max_errors: int = MAX_ERRORS_PER_ROW,
) -> pd.DataFrame:
    """
    Inject whitespace/casing anomalies.
    """

    def _distort(val):

        s = str(val)

        choice = random.randint(0, 3)

        if choice == 0:
            return "  " + s

        if choice == 1:
            return s + "   "

        if choice == 2:
            return s.upper()

        return s.lower()

    affected = []

    for idx in df.index:

        value = df.at[idx, col]

        if pd.isna(value):
            continue

        errors = _get_errors(df, idx)

        if not _under_cap(errors, max_errors):
            continue

        if coinflip(rate):

            df.at[idx, col] = _distort(value)
            affected.append(idx)

    append_error(
        df,
        affected,
        error_label,
        max_errors=max_errors,
    )

    return df


def duplicate_rows(
    df: pd.DataFrame,
    rate: float,
    error_label: str = "duplicate row",
) -> pd.DataFrame:
    """
    Duplicate rows and mark duplicated copies.
    """

    n = int(len(df) * rate)

    if n == 0:
        return df

    dupes = df.sample(
        n=n,
        random_state=42,
    ).copy(deep=True)

    for idx in dupes.index:

        errors = dupes.at[idx, "error_types"]

        if not isinstance(errors, list):
            errors = []

        else:
            errors = errors.copy()

        if error_label not in errors:
            errors.append(error_label)

        dupes.at[idx, "error_types"] = errors

    return pd.concat(
        [df, dupes],
        ignore_index=True,
    )
