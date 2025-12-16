import pandas as pd

from quantmaster.features.volatility import har_rv, realized_variance


def test_realized_variance_shape() -> None:
    idx = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame({"close": range(1, 51)}, index=idx)

    rv = realized_variance(df)

    assert isinstance(rv, pd.Series)
    assert rv.index.equals(df.index)
    assert rv.name == "rv"


def test_har_rv_columns_and_index() -> None:
    idx = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame({"close": range(1, 51)}, index=idx)

    out = har_rv(df, weekly_window=5, monthly_window=22)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert list(out.columns) == ["har_rv_d", "har_rv_w", "har_rv_m"]
