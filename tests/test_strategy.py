import pandas as pd

from backtest.engine import evaluate_trade
from backtest.performance import by_direction, by_entry_window, summary
from backtest.session import run_session
from data.loader import load_ohlcv_csv
from strategy.anchor import detect_anchor
from strategy.displacement import has_displacement
from strategy.market_structure import structure_state
from strategy.targets import rr_target
from strategy.time_windows import candle_window_duration, expected_candle_count


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


def test_loader_normalizes_naive_timestamps_to_new_york(tmp_path):
    path = tmp_path / "data.csv"
    pd.DataFrame([
        {"timestamp": "2026-09-01 09:45", "open": 100, "high": 105, "low": 99, "close": 104, "volume": 1000},
    ]).to_csv(path, index=False)
    frame = load_ohlcv_csv(path)
    assert str(frame["timestamp"].dt.tz) == "America/New_York"


def test_session_keeps_first_break_and_records_setup_outcome():
    frame = pd.DataFrame([
        {"timestamp": "2026-09-01 08:45", "open": 100, "high": 104, "low": 98, "close": 102, "volume": 1000},
        {"timestamp": "2026-09-01 09:45", "open": 102, "high": 105, "low": 100, "close": 104, "volume": 1000},
        {"timestamp": "2026-09-01 10:00", "open": 104, "high": 108, "low": 103, "close": 107, "volume": 1000},
        {"timestamp": "2026-09-01 10:15", "open": 107, "high": 111, "low": 106, "close": 110, "volume": 1000},
        {"timestamp": "2026-09-01 10:30", "open": 110, "high": 116, "low": 109, "close": 115, "volume": 1000},
        {"timestamp": "2026-09-01 10:45", "open": 115, "high": 121, "low": 114, "close": 120, "volume": 1000},
        {"timestamp": "2026-09-01 11:00", "open": 120, "high": 165, "low": 119, "close": 160, "volume": 1000},
    ])
    result = run_session(frame)
    assert result is not None
    assert result.first_break == "bullish"
    assert result.first_confirmation == "bullish"
    assert result.outcome == "win"
    assert result.r_multiple == 2.0


def test_performance_summary():
    results = [
        evaluate_trade("long", 100, 99, 102, highs=[102], lows=[100]),
        evaluate_trade("short", 100, 101, 98, highs=[101], lows=[99]),
        evaluate_trade("long", 100, 99, 102, highs=[99], lows=[98]),
    ]
    stats = summary(results)
    assert stats["trades"] == 3
    assert stats["wins"] == 2
    assert stats["losses"] == 1
    assert stats["net_r"] == 3.0
    assert stats["profit_factor"] == 4.0
    assert stats["max_drawdown_r"] == 1.0
    assert stats["longest_win_streak"] == 2
    assert stats["longest_loss_streak"] == 1


def test_performance_breakdowns():
    results = [
        evaluate_trade("long", 100, 99, 102, highs=[102], lows=[100]),
        evaluate_trade("short", 100, 101, 98, highs=[100], lows=[98]),
    ]
    directions = by_direction(results)
    assert directions["long"]["wins"] == 1
    assert directions["short"]["wins"] == 1

    session = run_session(pd.DataFrame([
        {"timestamp": "2026-09-01 09:45", "open": 102, "high": 105, "low": 100, "close": 104},
        {"timestamp": "2026-09-01 10:00", "open": 104, "high": 108, "low": 103, "close": 107},
        {"timestamp": "2026-09-01 10:15", "open": 107, "high": 111, "low": 106, "close": 110},
        {"timestamp": "2026-09-01 10:30", "open": 110, "high": 116, "low": 109, "close": 115},
        {"timestamp": "2026-09-01 11:00", "open": 115, "high": 125, "low": 114, "close": 124},
    ]))
    assert session is not None
    windows = by_entry_window([session])
    assert "10:00" in windows


def test_original_model_is_45_candles_on_one_minute_bars():
    assert expected_candle_count(45, 1) == 45
    assert candle_window_duration(45, 1).total_seconds() == 45 * 60


def test_45_candles_on_15_minute_bars_is_not_45_minutes():
    assert expected_candle_count(45, 15) == 3
    assert candle_window_duration(45, 15).total_seconds() == 45 * 15 * 60
