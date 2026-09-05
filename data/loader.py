"""Historical OHLCV data loading and validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    """Load an OHLCV CSV and return a validated, timestamp-sorted DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")

    for column in REQUIRED_COLUMNS[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    if frame["timestamp"].duplicated().any():
        raise ValueError("Duplicate timestamps found in OHLCV data")
    if not frame["timestamp"].is_monotonic_increasing:
        frame = frame.sort_values("timestamp").reset_index(drop=True)

    invalid_range = (frame["high"] < frame["low"]) | (frame["high"] < frame["open"]) | (frame["high"] < frame["close"]) | (frame["low"] > frame["open"]) | (frame["low"] > frame["close"])
    if invalid_range.any():
        raise ValueError("Invalid OHLC ranges found")

    return frame
