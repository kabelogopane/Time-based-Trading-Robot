"""Historical OHLCV data loading and validation."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")
NEW_YORK = ZoneInfo("America/New_York")


def _normalize_timestamps(values: pd.Series) -> pd.Series:
    """Normalize timestamps to America/New_York.

    Naive timestamps are treated as New York local time. Timezone-aware
    timestamps are converted to New York time.
    """
    parsed = pd.to_datetime(values, errors="raise")
    if getattr(parsed.dt, "tz", None) is None:
        return parsed.dt.tz_localize(NEW_YORK)
    return parsed.dt.tz_convert(NEW_YORK)


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    """Load, validate, sort, and timezone-normalize an OHLCV CSV."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    frame["timestamp"] = _normalize_timestamps(frame["timestamp"])

    for column in REQUIRED_COLUMNS[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    if frame["timestamp"].duplicated().any():
        raise ValueError("Duplicate timestamps found in OHLCV data")
    if not frame["timestamp"].is_monotonic_increasing:
        frame = frame.sort_values("timestamp").reset_index(drop=True)

    invalid_range = (
        (frame["high"] < frame["low"])
        | (frame["high"] < frame["open"])
        | (frame["high"] < frame["close"])
        | (frame["low"] > frame["open"])
        | (frame["low"] > frame["close"])
    )
    if invalid_range.any():
        raise ValueError("Invalid OHLC ranges found")

    return frame
