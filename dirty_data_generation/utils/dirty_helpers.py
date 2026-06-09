import random

import pandas as pd

from dirty_data_generation.config.constants import MAX_ERRORS_PER_ROW


def coinflip(prob: float) -> bool:
    return random.random() < prob


def _under_cap(row, max_errors: int = MAX_ERRORS_PER_ROW) -> bool:
    """Check if a row still has room for more error types."""
    return len(set(row.get("error_types", []))) < max_errors


def inject_nulls(
    df: pd.DataFrame,
    mask: pd.Series,
    col: str,
    rate: float,
    error_label: str,
    max_errors: int = MAX_ERRORS_PER_ROW,
) -> pd.DataFrame:
    """
    Randomly set `col` to null for rows where `mask` is True, at the
    specified rate. Respects per-row error cap and deduplicates labels.
    """
    eligible = df.loc[mask & df.apply(lambda r: _under_cap(r, max_errors), axis=1)]
    null_mask = pd.Series(
        [coinflip(rate) for _ in range(len(eligible))],
        index=eligible.index,
    )
    affected = null_mask[null_mask].index
    df.loc[affected, col] = None
    for idx in affected:
        if error_label not in df.at[idx, "error_types"]:
            df.at[idx, "error_types"].append(error_label)
    return df


def inject_whitespace(
    df: pd.DataFrame,
    col: str,
    rate: float,
    error_label: str = "formatting anomaly",
    max_errors: int = MAX_ERRORS_PER_ROW,
) -> pd.DataFrame:
    """
    Add whitespace/casing anomalies. Skips rows already at error cap
    and deduplicates error labels.
    """

    def _distort(val: str) -> str:
        s = str(val)
        choice = random.randint(0, 3)
        if choice == 0:
            return "  " + s
        elif choice == 1:
            return s + "   "
        elif choice == 2:
            return s.upper()
        else:
            return s.lower()

    valid_idx = df[
        df[col].notna() & df.apply(lambda r: _under_cap(r, max_errors), axis=1)
    ].index

    corrupt_mask = pd.Series(
        [coinflip(rate) for _ in range(len(valid_idx))],
        index=valid_idx,
    )
    affected = corrupt_mask[corrupt_mask].index

    for idx in affected:
        df.at[idx, col] = _distort(df.at[idx, col])
        if error_label not in df.at[idx, "error_types"]:
            df.at[idx, "error_types"].append(error_label)
    return df


def duplicate_rows(
    df: pd.DataFrame,
    rate: float,
    error_label: str = "duplicate row",
) -> pd.DataFrame:
    """
    Randomly duplicate rows and mark duplicates with an error label.
    """
    n = int(len(df) * rate)
    if n == 0:
        return df
    dupes = df.sample(n=n, random_state=42).copy()
    for idx in dupes.index:
        existing = list(dupes.at[idx, "error_types"])
        if error_label not in existing:
            existing.append(error_label)
        dupes.at[idx, "error_types"] = existing
    return pd.concat([df, dupes], ignore_index=True)


def append_error(df: pd.DataFrame, indices, error_label: str) -> None:
    """Append an error label to rows by index, deduplicating."""
    for idx in indices:
        if error_label not in df.at[idx, "error_types"]:
            df.at[idx, "error_types"].append(error_label)
