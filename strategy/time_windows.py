"""Time-window logic for the original 45-minute model."""

from datetime import datetime, time
from zoneinfo import ZoneInfo

# The model is now expressed in U.S. Eastern Time (New York).
# ZoneInfo handles EST/EDT daylight-saving changes automatically.
TIMEZONE = ZoneInfo("America/New_York")
WINDOWS = ("08:45", "09:45", "10:45", "11:45", "12:45", "13:45", "15:45")


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
    """Return the latest model window reached at the timestamp."""
    local = timestamp.astimezone(TIMEZONE)
    current = local.time().hour * 60 + local.time().minute

    candidates = []
    for label in WINDOWS:
        t = parse_hhmm(label)
        minutes = t.hour * 60 + t.minute
        if minutes <= current:
            candidates.append((minutes, label))

    return max(candidates)[1] if candidates else None
