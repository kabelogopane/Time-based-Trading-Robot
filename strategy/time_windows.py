"""Time and candle-window logic for the original 45-candle model."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/New_York")
WINDOWS = ("08:45", "09:45", "10:45", "11:45", "12:45", "13:45", "15:45")
DEFAULT_BAR_INTERVAL_MINUTES = 1
DEFAULT_CANDLES_PER_WINDOW = 45


def parse_hhmm(value: str) -> time:
    """Convert HH:MM text to a time object."""
    hour, minute = map(int, value.split(":"))
    return time(hour, minute)


def session_window_times() -> tuple[time, ...]:
    """Return configured model times as time objects."""
    return tuple(parse_hhmm(value) for value in WINDOWS)


def is_model_time(timestamp: datetime, hhmm: str) -> bool:
    """Return True when a timestamp matches a configured model time."""
    local = timestamp.astimezone(TIMEZONE)
    target = parse_hhmm(hhmm)
    return local.time().hour == target.hour and local.time().minute == target.minute


def model_window(timestamp: datetime) -> str | None:
    """Return the latest model clock window reached at the timestamp."""
    local = timestamp.astimezone(TIMEZONE)
    current = local.time().hour * 60 + local.time().minute
    candidates = []
    for label in WINDOWS:
        t = parse_hhmm(label)
        minutes = t.hour * 60 + t.minute
        if minutes <= current:
            candidates.append((minutes, label))
    return max(candidates)[1] if candidates else None


def candle_window_duration(
    candles_per_window: int = DEFAULT_CANDLES_PER_WINDOW,
    bar_interval_minutes: int = DEFAULT_BAR_INTERVAL_MINUTES,
) -> timedelta:
    """Return the clock duration represented by a candle-count window.

    The original model is candle-based. For example, 45 one-minute candles
    represent 45 minutes. Changing the chart timeframe changes the clock
    duration unless the candle count is also changed.
    """
    if candles_per_window < 1:
        raise ValueError("candles_per_window must be at least 1")
    if bar_interval_minutes < 1:
        raise ValueError("bar_interval_minutes must be at least 1")
    return timedelta(minutes=candles_per_window * bar_interval_minutes)


def expected_candle_count(
    window_minutes: int = 45,
    bar_interval_minutes: int = DEFAULT_BAR_INTERVAL_MINUTES,
) -> int:
    """Return how many bars are expected inside a clock-time window."""
    if window_minutes < 1 or bar_interval_minutes < 1:
        raise ValueError("window_minutes and bar_interval_minutes must be at least 1")
    if window_minutes % bar_interval_minutes:
        raise ValueError("window_minutes must be divisible by bar_interval_minutes")
    return window_minutes // bar_interval_minutes
