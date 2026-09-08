import pandas as pd

from strategy.setup_filters import (
    directional_displacement,
    find_anchor_sweep,
    find_fvg,
    has_mss,
)


def test_anchor_sweep_requires_reclaim():
    frame = pd.DataFrame([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1},
        {"open": 104, "high": 105, "low": 98, "close": 101, "volume": 1},
    ])
    sweep = find_anchor_sweep(frame, 105, 99)
    assert sweep is not None
    assert sweep.direction == "long"
    assert sweep.index == 1
    assert sweep.price == 98


def test_displacement_requires_direction_and_body_strength():
    bullish = pd.Series({"open": 100, "high": 105, "low": 99, "close": 105})
    weak = pd.Series({"open": 100, "high": 105, "low": 99, "close": 101})
    assert directional_displacement(bullish) == "bullish"
    assert directional_displacement(weak) is None


def test_mss_uses_only_completed_previous_candles():
    frame = pd.DataFrame([
        {"open": 100, "high": 102, "low": 99, "close": 101},
        {"open": 101, "high": 103, "low": 100, "close": 102},
        {"open": 102, "high": 104, "low": 101, "close": 103},
        {"open": 103, "high": 106, "low": 102, "close": 105},
    ])
    assert has_mss(frame, 0, "long", lookback=3) == 3


def test_bullish_fvg_is_detected():
    frame = pd.DataFrame([
        {"open": 100, "high": 101, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 100, "close": 102},
        {"open": 103, "high": 105, "low": 103, "close": 104},
    ])
    fvg = find_fvg(frame, 2, "long")
    assert fvg is not None
    assert fvg.lower == 101
    assert fvg.upper == 103
