import pandas as pd

from strategy.pipeline import scan_execution_window


def test_pipeline_returns_none_when_window_has_no_confirmed_setup():
    candles = pd.DataFrame([
        {"timestamp": "2026-09-01 10:00", "open": 100, "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-09-01 10:01", "open": 100, "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-09-01 10:02", "open": 100, "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-09-01 10:03", "open": 100, "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-09-01 10:04", "open": 100, "high": 101, "low": 99, "close": 100},
        {"timestamp": "2026-09-01 10:05", "open": 100, "high": 101, "low": 99, "close": 100},
    ])
    assert scan_execution_window(candles) is None
