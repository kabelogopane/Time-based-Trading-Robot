import pandas as pd

from data.validate import assess_quality


def make_frame(interval_minutes=1):
    timestamps = pd.date_range("2026-09-01 09:45", periods=4, freq=f"{interval_minutes}min", tz="America/New_York")
    return pd.DataFrame({
        "timestamp": timestamps,
        "open": [100, 101, 102, 103],
        "high": [101, 102, 103, 104],
        "low": [99, 100, 101, 102],
        "close": [100.5, 101.5, 102.5, 103.5],
        "volume": [10, 11, 12, 13],
    })


def test_valid_one_minute_data_is_ready():
    quality = assess_quality(make_frame())
    assert quality.interval_minutes == 1.0
    assert quality.duplicate_timestamps == 0
    assert quality.gaps == 0
    assert quality.invalid_ohlc == 0
    assert quality.ready_for_45_candle_model is True


def test_fifteen_minute_data_is_not_ready():
    quality = assess_quality(make_frame(15))
    assert quality.interval_minutes == 15.0
    assert quality.ready_for_45_candle_model is False


def test_gap_is_detected():
    frame = make_frame().drop(index=2).reset_index(drop=True)
    quality = assess_quality(frame)
    assert quality.gaps == 1
    assert quality.ready_for_45_candle_model is False


def test_duplicate_is_detected():
    frame = pd.concat([make_frame(), make_frame().iloc[[1]]], ignore_index=True)
    quality = assess_quality(frame)
    assert quality.duplicate_timestamps == 1
    assert quality.ready_for_45_candle_model is False


def test_invalid_ohlc_is_detected():
    frame = make_frame()
    frame.loc[0, "high"] = 90
    quality = assess_quality(frame)
    assert quality.invalid_ohlc == 1
    assert quality.ready_for_45_candle_model is False
