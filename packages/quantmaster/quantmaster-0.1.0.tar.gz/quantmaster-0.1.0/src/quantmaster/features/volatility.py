from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_positive_int


def realized_variance(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    price = get_price_series(data, price_col=price_col).astype(float)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    rv = rets.pow(2)
    rv.name = "rv"
    return rv


def har_rv(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    weekly_window: int = 5,
    monthly_window: int = 22,
    prefix: str = "har_rv",
) -> pd.DataFrame:
    weekly_window = validate_positive_int(weekly_window, name="weekly_window")
    monthly_window = validate_positive_int(monthly_window, name="monthly_window")

    rv = realized_variance(data, price_col=price_col)

    out = pd.DataFrame(index=rv.index)
    out[f"{prefix}_d"] = rv
    out[f"{prefix}_w"] = rv.rolling(weekly_window).mean()
    out[f"{prefix}_m"] = rv.rolling(monthly_window).mean()
    return out
