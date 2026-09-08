import pandas as pd

from backtest.regime import all_regime_summaries, build_regime_table
from backtest.session import run_session


def session_frame(anchor_low=100, anchor_high=105, break_at=1, direction="bullish"):
    rows = [
        {"timestamp": "2026-09-01 09:45", "open": 102, "high": anchor_high, "low": anchor_low, "close": 103},
    ]
    for i in range(5):
        timestamp = pd.Timestamp("2026-09-01 10:00") + pd.Timedelta(minutes=15 * i)
        if direction == "bullish":
            close = 106 if i >= break_at else 103
            rows.append({"timestamp": timestamp, "open": close - 1, "high": close + 2, "low": close - 1.5, "close": close})
        else:
            close = 99 if i >= break_at else 102
            rows.append({"timestamp": timestamp, "open": close + 1, "high": close + 1.5, "low": close - 2, "close": close})
    return pd.DataFrame(rows)


def test_regime_features_do_not_change_trade_result_fields():
    result = run_session(session_frame())
    assert result is not None
    assert result.first_break == "bullish"
    assert result.first_break_candles == 1
    assert result.first_break_timestamp is not None
    assert result.anchor_high == 105
    assert result.anchor_low == 100


def test_regime_table_creates_range_speed_break_and_path_labels():
    result = run_session(session_frame())
    assert result is not None
    table = build_regime_table([result])
    assert table.loc[0, "anchor_range_regime"] == "small"
    assert table.loc[0, "break_speed_regime"] == "fast"
    assert table.loc[0, "first_break_regime"] == "bullish"
    assert table.loc[0, "path_regime"] == "continued_away"


def test_regime_summary_uses_same_r_multiple_outcomes():
    result = run_session(session_frame())
    assert result is not None
    summaries = all_regime_summaries([result])
    row = summaries["break_speed"].iloc[0]
    assert row["sessions"] == 1
    assert row["closed_trades"] == int(result.outcome in {"win", "loss"})
    assert row["net_r"] == result.r_multiple if result.outcome in {"win", "loss"} else 0
