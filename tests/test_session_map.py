import pandas as pd

from strategy.session_map import build_session_map, session_map_frame


def test_session_map_records_all_model_times():
    frame = pd.DataFrame([
        {"timestamp": "2026-09-01 08:45", "open": 100, "high": 102, "low": 99, "close": 101},
        {"timestamp": "2026-09-01 09:45", "open": 101, "high": 105, "low": 100, "close": 104},
        {"timestamp": "2026-09-01 10:45", "open": 104, "high": 110, "low": 103, "close": 109},
        {"timestamp": "2026-09-01 11:45", "open": 109, "high": 112, "low": 108, "close": 111},
        {"timestamp": "2026-09-01 13:45", "open": 111, "high": 114, "low": 110, "close": 113},
        {"timestamp": "2026-09-01 15:45", "open": 113, "high": 115, "low": 112, "close": 114},
    ])
    result = build_session_map(frame)
    assert [item.time for item in result] == ["08:45", "09:45", "10:45", "11:45", "12:45", "13:45", "15:45"]
    assert result[1].label == "anchor"
    assert result[1].high == 105.0
    assert result[4].status == "missing"
    assert result[4].close is None


def test_session_map_frame_is_dashboard_ready():
    frame = pd.DataFrame([
        {"timestamp": "2026-09-01 09:45", "open": 100, "high": 105, "low": 99, "close": 104},
    ])
    result = session_map_frame(frame)
    assert list(result.columns) == ["time", "label", "candle_count", "open", "high", "low", "close", "status"]
    assert len(result) == 7
