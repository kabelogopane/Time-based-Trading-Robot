"""Validation helpers for the original 45-candle research model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time

import pandas as pd

EXPECTED_INTERVAL_MINUTES = 1
RESEARCH_TIMEZONE = "America/New_York"
SESSION_START = time(8, 45)
SESSION_END = time(15, 45)


@dataclass(frozen=True)
class DataQuality:
    rows: int
    interval_minutes: float | None
    duplicate_timestamps: int
    gaps: int
    invalid_ohlc: int
    ready_for_45_candle_model: bool


def _session_gaps(
    frame: pd.DataFrame,
    expected_interval_minutes: int,
    timezone: str,
    session_start: time,
    session_end: time,
) -> int:
    """Count missing bars only inside each New York research session.

    Overnight, weekend, and other out-of-session breaks are not treated as
    data gaps because the market is not expected to provide continuous
    one-minute bars across those boundaries.
    """
    local = frame["timestamp"]
    if getattr(local.dt, "tz", None) is None:
        local = local.dt.tz_localize(timezone)
    else:
        local = local.dt.tz_convert(timezone)

    session = frame.copy()
    session["_local_timestamp"] = local
    session["_date"] = local.dt.date
    session["_time"] = local.dt.time
    session = session[
        (session["_time"] >= session_start)
        & (session["_time"] <= session_end)
    ]

    gaps = 0
    for _, day in session.groupby("_date"):
        deltas = day["_local_timestamp"].sort_values().diff().dropna()
        minutes = deltas.dt.total_seconds().div(60)
        gaps += int((minutes > expected_interval_minutes).sum())
    return gaps


def assess_quality(
    candles: pd.DataFrame,
    expected_interval_minutes: int = EXPECTED_INTERVAL_MINUTES,
    timezone: str = RESEARCH_TIMEZONE,
    session_start: time = SESSION_START,
    session_end: time = SESSION_END,
) -> DataQuality:
    """Assess whether OHLCV data is usable by the 45-candle model.

    Gap checks are session-aware. This prevents normal overnight/weekend
    breaks from making otherwise valid one-minute research data fail.
    """
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if expected_interval_minutes < 1:
        raise ValueError("expected_interval_minutes must be at least 1")
    if session_start >= session_end:
        raise ValueError("session_start must be earlier than session_end")

    frame = candles.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")
    frame = frame.sort_values("timestamp").reset_index(drop=True)

    deltas = frame["timestamp"].diff().dropna().dt.total_seconds().div(60)
    interval = float(deltas.median()) if not deltas.empty else None
    duplicates = int(frame["timestamp"].duplicated().sum())
    gaps = _session_gaps(
        frame,
        expected_interval_minutes=expected_interval_minutes,
        timezone=timezone,
        session_start=session_start,
        session_end=session_end,
    )
    invalid = int((
        (frame["high"] < frame["low"])
        | (frame["high"] < frame["open"])
        | (frame["high"] < frame["close"])
        | (frame["low"] > frame["open"])
        | (frame["low"] > frame["close"])
    ).sum())
    ready = bool(
        len(frame) > 0
        and interval == expected_interval_minutes
        and duplicates == 0
        and gaps == 0
        and invalid == 0
    )
    return DataQuality(len(frame), interval, duplicates, gaps, invalid, ready)
