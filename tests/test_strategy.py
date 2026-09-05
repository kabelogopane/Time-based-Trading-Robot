from datetime import datetime

import pandas as pd

from strategy.anchor import detect_anchor
from strategy.displacement import has_displacement
from strategy.market_structure import structure_state
from strategy.targets import rr_target
from backtest.engine import evaluate_trade


def sample_candles():
    return pd.DataFrame([
        {"timestamp": "2026-09-01 09:30", "open": 100, "high": 102, "low": 99, "close": 101},
        {"timestamp": "2026-09-01 09:45", "open": 101, "high": 105, "low": 100, "close": 104},
        {"timestamp": "2026-09-01 10:00", "open": 104, "high": 108, "low": 103, "close": 107},
        {"timestamp": "2026-09-01 10:15", "open": 107, "high": 111, "low": 106, "close": 110},
        {"timestamp": "2026-09-01 10:30", "open": 110, "high": 114, "low": 109, "close": 113},
    ])


def test_anchor_is_detected():
    anchor = detect_anchor(sample_candles())
    assert anchor is not None
    assert anchor.high == 105
    assert anchor.low == 100


def test_bullish_structure_is_detected():
    assert structure_state(sample_candles(), lookback=3) == "bullish"


def test_displacement_ratio():
    candle = sample_candles().iloc[1]
    assert has_displacement(candle, threshold=0.5)


def test_two_to_one_target_for_long():
    assert rr_target(104, 100, 2.0, "long") == 112


def test_target_hit_returns_win():
    result = evaluate_trade("long", 104, 100, 112, highs=[108, 113], lows=[103, 106])
    assert result.outcome == "win"
    assert result.r_multiple == 2.0
