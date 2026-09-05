import pandas as pd

from strategy.market_events import build_market_events, market_events_frame


def test_market_events_map_break_structure_displacement_and_confirmation():
    frame = pd.DataFrame([
        {"timestamp": "2026-09-01 08:45", "open": 99, "high": 101, "low": 98, "close": 100},
        {"timestamp": "2026-09-01 09:45", "open": 100, "high": 105, "low": 99, "close": 104},
        {"timestamp": "2026-09-01 10:45", "open": 104, "high": 111, "low": 103.8, "close": 110},
        {"timestamp": "2026-09-01 11:45", "open": 110, "high": 112, "low": 108, "close": 111},
    ])

    events = build_market_events(frame)
    anchor = next(event for event in events if event.time == "09:45")
    reaction = next(event for event in events if event.time == "10:45")
    midday = next(event for event in events if event.time == "12:45")

    assert anchor.liquidity_event == "anchor_set"
    assert reaction.liquidity_reference == "anchor_high"
    assert reaction.liquidity_event == "buy_side_reference_taken"
    assert reaction.break_direction == "bullish"
    assert reaction.structure == "bullish"
    assert reaction.displacement is True
    assert reaction.confirmation == "bullish"
    assert midday.status == "missing"


def test_market_events_return_missing_anchor_status():
    frame = pd.DataFrame([
        {"timestamp": "2026-09-01 08:45", "open": 99, "high": 101, "low": 98, "close": 100},
        {"timestamp": "2026-09-01 10:45", "open": 100, "high": 102, "low": 99, "close": 101},
    ])

    events = build_market_events(frame)

    assert len(events) == 7
    assert all(event.status == "missing_anchor" for event in events)


def test_market_events_frame_is_dashboard_ready():
    frame = pd.DataFrame([
        {"timestamp": "2026-09-01 09:45", "open": 100, "high": 105, "low": 99, "close": 104},
    ])

    result = market_events_frame(frame)

    assert list(result.columns) == [
        "time", "label", "liquidity_reference", "liquidity_event",
        "break_direction", "structure", "displacement", "confirmation", "status",
    ]
    assert len(result) == 7
