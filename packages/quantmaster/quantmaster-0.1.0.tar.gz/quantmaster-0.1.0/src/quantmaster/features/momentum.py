from __future__ import annotations

import pandas as pd

from quantmaster.features.utils import get_price_series, validate_positive_int


def rsi(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 14,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)

    delta = price.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

    rs = avg_gain / avg_loss
    out = 100 - (100 / (1 + rs))

    out = out.where(avg_loss != 0, 100.0)
    out = out.where(avg_gain != 0, 0.0)

    out.name = f"rsi_{window}"
    return out
