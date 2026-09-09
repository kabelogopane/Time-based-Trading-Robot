import pandas as pd

from strategy.timeframe import aggregate_to_3m, aggregate_to_45m, normalize_new_york


def make_candles(start="2026-01-05 09:42", periods=6):
    timestamps = pd.date_range(start, periods=periods, freq="1min")
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": range(100, 100 + periods),
            "high": range(101, 101 + periods),
            "low": range(99, 99 + periods),
            "close": range(100, 100 + periods),
            "volume": [10] * periods,
        }
    )


def test_normalize_naive_timestamps_to_new_york():
    result = normalize_new_york(make_candles())
    assert str(result["timestamp"].dt.tz) == "America/New_York"


def test_aggregate_to_3m_uses_ohlcv_rules():
    result = aggregate_to_3m(make_candles())
    assert len(result) == 2
    first = result.iloc[0]
    assert first["open"] == 100
    assert first["high"] == 103
    assert first["low"] == 99
    assert first["close"] == 102
    assert first["volume"] == 30


def test_aggregate_to_45m_is_aligned_at_45_minutes():
    result = aggregate_to_45m(make_candles("2026-01-05 09:45", periods=45))
    assert len(result) == 1
    assert result.iloc[0]["timestamp"].strftime("%H:%M") == "09:45"
    assert result.iloc[0]["open"] == 100
    assert result.iloc[0]["close"] == 144
