import pandas as pd

from quantmaster.features.momentum import rsi


def test_rsi_shape_and_name() -> None:
    idx = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame(
        {
            "open": range(1, 51),
            "high": range(2, 52),
            "low": range(0, 50),
            "close": range(1, 51),
            "volume": [100] * 50,
        },
        index=idx,
    )

    out = rsi(df, window=14)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "rsi_14"

    bounded = out.dropna()
    assert (bounded >= 0).all()
    assert (bounded <= 100).all()
