"""
Maintains a registry of generated error types and their affected columns.
"""

from __future__ import annotations

import json
from pathlib import Path

ERROR_REGISTRY: dict[str, dict] = {}

DEFAULT_REGISTRY_PATH = (
    Path("dirty_data_generation") / "dirty_data" / "error_metadata.json"
)


def register_error(
    error_label: str,
    columns: list[str],
) -> None:
    """
    Register the affected columns for an error type.

    Raises an exception if the same error is registered with
    different columns.
    """
    columns = sorted(set(columns))
    existing = ERROR_REGISTRY.get(error_label)

    if existing is None:
        ERROR_REGISTRY[error_label] = {
            "columns": columns,
        }
        return

    if existing["columns"] != columns:
        raise ValueError(
            f"Inconsistent column mapping for '{error_label}'.\n"
            f"Existing: {existing['columns']}\n"
            f"New: {columns}"
        )


def save_registry(
    path: Path = DEFAULT_REGISTRY_PATH,
) -> None:
    """
    Persist the registry to disk.
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            ERROR_REGISTRY,
            f,
            indent=4,
            sort_keys=True,
        )


def load_registry(
    path: Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, dict]:
    """
    Load registry from disk.
    """
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)
