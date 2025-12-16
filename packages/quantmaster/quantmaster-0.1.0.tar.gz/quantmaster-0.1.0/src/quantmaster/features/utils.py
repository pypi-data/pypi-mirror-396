from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

DEFAULT_OHLCV_COLUMNS: tuple[str, ...] = ("open", "high", "low", "close", "volume")


def validate_positive_int(value: int, *, name: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be int, got {type(value).__name__}")
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")
    return value


def validate_non_negative_int(value: int, *, name: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def validate_columns(data: pd.DataFrame, *, required: Iterable[str]) -> None:
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def validate_ohlcv(data: pd.DataFrame, *, required: Iterable[str] = DEFAULT_OHLCV_COLUMNS) -> None:
    validate_columns(data, required=required)


def get_price_series(data: pd.DataFrame | pd.Series, *, price_col: str = "close") -> pd.Series:
    if isinstance(data, pd.Series):
        series = data
    else:
        if price_col not in data.columns:
            raise KeyError(f"Column '{price_col}' not found in DataFrame")
        series = data[price_col]

    return pd.to_numeric(series, errors="coerce")
