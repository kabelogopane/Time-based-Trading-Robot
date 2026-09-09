import pandas as pd

from strategy.liquidity import (
    find_liquidity_sweeps,
    swept_high,
    swept_low,
)


def test_swept_high():
    assert swept_high(100, 103, 99)
    assert not swept_high(100, 99, 98)


def test_swept_low():
    assert swept_low(100, 97, 101)
    assert not swept_low(100, 101, 102)


def test_find_high_liquidity_sweep():
    candles = pd.DataFrame([
        {"timestamp": "2026-09-01 10:00", "high": 100, "low": 98, "close": 99},
        {"timestamp": "2026-09-01 10:01", "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-09-01 10:02", "high": 103, "low": 99, "close": 99.5},
    ])
    sweeps = find_liquidity_sweeps(candles, lookback=2)
    assert len(sweeps) == 1
    assert sweeps[0].direction == "high"
    assert sweeps[0].level == 101


def test_find_low_liquidity_sweep():
    candles = pd.DataFrame([
        {"timestamp": "2026-09-01 10:00", "high": 102, "low": 100, "close": 101},
        {"timestamp": "2026-09-01 10:01", "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-09-01 10:02", "high": 100, "low": 97, "close": 100.5},
    ])
    sweeps = find_liquidity_sweeps(candles, lookback=2)
    assert len(sweeps) == 1
    assert sweeps[0].direction == "low"
    assert sweeps[0].level == 99


def test_invalid_lookback():
    candles = pd.DataFrame([{"high": 1, "low": 0, "close": 0.5}])
    try:
        find_liquidity_sweeps(candles, lookback=0)
        assert False
    except ValueError:
        assert True
