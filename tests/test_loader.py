import pandas as pd

from data.loader import load_ohlcv_csv


def test_loader_accepts_datetime_column(tmp_path):
    source = tmp_path / "SPX500_1m.csv"
    pd.DataFrame([
        {
            "datetime": "2026-07-08T13:45:00+00:00",
            "open": 100,
            "high": 105,
            "low": 99,
            "close": 104,
            "volume": 1,
        }
    ]).to_csv(source, index=False)

    result = load_ohlcv_csv(source)

    assert list(result.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
    assert str(result.loc[0, "timestamp"]) == "2026-07-08 09:45:00-04:00"
