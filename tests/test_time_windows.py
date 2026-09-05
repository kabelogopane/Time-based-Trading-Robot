import pandas as pd

from backtest.time_windows import build_45m_windows


def candles():
    return pd.DataFrame([
        {"timestamp": "2026-09-01 09:45", "open": 100, "high": 105, "low": 99, "close": 104},
        {"timestamp": "2026-09-01 10:00", "open": 104, "high": 108, "low": 103, "close": 107},
        {"timestamp": "2026-09-01 10:15", "open": 107, "high": 111, "low": 106, "close": 110},
        {"timestamp": "2026-09-01 10:30", "open": 110, "high": 114, "low": 109, "close": 112},
        {"timestamp": "2026-09-01 10:45", "open": 112, "high": 116, "low": 111, "close": 115},
        {"timestamp": "2026-09-01 11:00", "open": 115, "high": 118, "low": 113, "close": 114},
        {"timestamp": "2026-09-01 11:15", "open": 114, "high": 115, "low": 110, "close": 111},
    ])


def test_builds_consecutive_45_minute_windows_from_anchor():
    result = build_45m_windows(candles())

    assert [(item.window_start, item.window_end) for item in result[:3]] == [
        ("09:45", "10:30"),
        ("10:30", "11:15"),
        ("11:15", "12:00"),
    ]


def test_first_window_includes_anchor_and_uses_ohlc_extremes():
    result = build_45m_windows(candles())
    first = result[0]

    assert first.candles == 3
    assert first.open == 100
    assert first.high == 111
    assert first.low == 99
    assert first.close == 110
    assert first.range == 12
    assert first.direction == "bullish"


def test_boundary_candle_belongs_to_next_window():
    result = build_45m_windows(candles())

    assert result[0].close == 110
    assert result[1].open == 110


def test_windows_do_not_mix_calendar_days():
    frame = candles()
    frame = pd.concat([
        frame,
        pd.DataFrame([
            {"timestamp": "2026-09-02 09:45", "open": 200, "high": 205, "low": 199, "close": 204},
            {"timestamp": "2026-09-02 10:00", "open": 204, "high": 208, "low": 203, "close": 207},
        ]),
    ], ignore_index=True)

    result = build_45m_windows(frame)
    assert result[0].date == "2026-09-01"
    assert result[-1].date == "2026-09-02"
    # The anchor candle starts the new day's first window.
    assert result[-1].open == 200
