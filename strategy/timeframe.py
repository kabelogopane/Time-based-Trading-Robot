"""Deterministic timeframe conversion for research OHLCV data."""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pandas as pd

NEW_YORK = ZoneInfo("America/New_York")


def normalize_new_york(candles: pd.DataFrame) -> pd.DataFrame:
    """Return candles with timezone-aware timestamps in New York time."""
    if "timestamp" not in candles.columns:
        raise ValueError("Missing required column: timestamp")

    frame = candles.copy()
    parsed = pd.to_datetime(frame["timestamp"], errors="raise")
    if parsed.dt.tz is None:
        frame["timestamp"] = parsed.dt.tz_localize(NEW_YORK)
    else:
        frame["timestamp"] = parsed.dt.tz_convert(NEW_YORK)
    return frame.sort_values("timestamp").reset_index(drop=True)


def aggregate_ohlcv(candles: pd.DataFrame, minutes: int, offset: str = "0min") -> pd.DataFrame:
    """Aggregate OHLCV candles into a deterministic minute timeframe.

    Naive timestamps are interpreted as America/New_York. Existing timezone-aware
    timestamps are converted to New York. Only available source bars are used;
    missing bars are not silently filled.
    """
    if minutes < 1:
        raise ValueError("minutes must be at least 1")

    frame = normalize_new_york(candles)
    required = {"open", "high", "low", "close"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    indexed = frame.set_index("timestamp")
    aggregations = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
    }
    if "volume" in indexed.columns:
        aggregations["volume"] = "sum"

    result = indexed.resample(
        f"{minutes}min",
        origin="start_day",
        offset=offset,
        label="left",
        closed="left",
    ).agg(aggregations)

    result = result.dropna(subset=["open", "high", "low", "close"]).reset_index()
    return result


def aggregate_to_3m(candles: pd.DataFrame) -> pd.DataFrame:
    """Convert source OHLCV candles to 3-minute execution candles."""
    return aggregate_ohlcv(candles, 3)


def aggregate_to_45m(candles: pd.DataFrame) -> pd.DataFrame:
    """Convert source OHLCV candles to 45-minute anchor candles aligned at :45."""
    # 45-minute bins from the top of the hour produce 09:45, 10:30, 11:15, ...
    return aggregate_ohlcv(candles, 45, offset="0min")
