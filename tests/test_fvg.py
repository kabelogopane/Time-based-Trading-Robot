import pandas as pd

from strategy.fvg import FairValueGap, detect_fvg, find_fvgs, fvg_retested


def candle(high, low):
    return pd.Series({"high": high, "low": low})


def test_bullish_fvg_is_detected():
    gap = detect_fvg(candle(105, 100), candle(112, 108))
    assert gap is not None
    assert gap.direction == "bullish"
    assert gap.lower == 105
    assert gap.upper == 108
    assert gap.size == 3


def test_bearish_fvg_is_detected():
    gap = detect_fvg(candle(105, 100), candle(97, 94))
    assert gap is not None
    assert gap.direction == "bearish"
    assert gap.lower == 97
    assert gap.upper == 100
    assert gap.size == 3


def test_no_fvg_when_ranges_overlap():
    gap = detect_fvg(candle(105, 100), candle(108, 103))
    assert gap is None


def test_find_fvgs_returns_detected_gaps():
    candles = pd.DataFrame([
        {"timestamp": "2026-09-01 10:00", "high": 105, "low": 100},
        {"timestamp": "2026-09-01 10:01", "high": 110, "low": 104},
        {"timestamp": "2026-09-01 10:02", "high": 115, "low": 108},
    ])
    gaps = find_fvgs(candles)
    assert len(gaps) == 1
    assert gaps[0].direction == "bullish"
    assert gaps[0].lower == 105
    assert gaps[0].upper == 108


def test_fvg_contains_price():
    gap = FairValueGap("bullish", 105, 108)
    assert gap.contains(105)
    assert gap.contains(106.5)
    assert gap.contains(108)
    assert not gap.contains(104.9)


def test_fvg_retest_is_detected_after_third_candle():
    candles = pd.DataFrame([
        {"timestamp": "2026-09-01 10:00", "high": 105, "low": 100},
        {"timestamp": "2026-09-01 10:01", "high": 110, "low": 104},
        {"timestamp": "2026-09-01 10:02", "high": 115, "low": 108},
        {"timestamp": "2026-09-01 10:03", "high": 112, "low": 106},
    ])
    gap = find_fvgs(candles)[0]
    assert fvg_retested(gap, candles)


def test_fvg_retest_is_not_counted_before_third_candle():
    candles = pd.DataFrame([
        {"timestamp": "2026-09-01 10:00", "high": 105, "low": 100},
        {"timestamp": "2026-09-01 10:01", "high": 110, "low": 104},
        {"timestamp": "2026-09-01 10:02", "high": 115, "low": 108},
    ])
    gap = find_fvgs(candles)[0]
    assert not fvg_retested(gap, candles)
