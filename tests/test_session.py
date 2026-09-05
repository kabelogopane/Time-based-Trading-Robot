import pandas as pd

from backtest.session import run_session


def test_session_finds_bullish_confirmed_setup():
    frame = pd.DataFrame([
        {"timestamp": "2026-09-01 09:45", "open": 100, "high": 105, "low": 99, "close": 104, "volume": 1},
        # Strong enough body/range ratio for the model's displacement rule.
        {"timestamp": "2026-09-01 10:00", "open": 104, "high": 108, "low": 103.8, "close": 107, "volume": 1},
        {"timestamp": "2026-09-01 10:15", "open": 107, "high": 112, "low": 106, "close": 111, "volume": 1},
        {"timestamp": "2026-09-01 10:30", "open": 111, "high": 116, "low": 110, "close": 115, "volume": 1},
        {"timestamp": "2026-09-01 10:45", "open": 115, "high": 120, "low": 114, "close": 119, "volume": 1},
    ])

    result = run_session(frame)

    assert result is not None
    assert result.first_break == "bullish"
    assert result.first_confirmation == "bullish"
    assert result.entry == 107.0
    assert result.invalidation == 99.0
    assert result.target == 123.0
