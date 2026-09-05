"""Validation helpers for the original 45-candle research model."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

EXPECTED_INTERVAL_MINUTES = 1


@dataclass(frozen=True)
class DataQuality:
    rows: int
    interval_minutes: float | None
    duplicate_timestamps: int
    gaps: int
    invalid_ohlc: int
    ready_for_45_candle_model: bool


def assess_quality(candles: pd.DataFrame, expected_interval_minutes: int = EXPECTED_INTERVAL_MINUTES) -> DataQuality:
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if expected_interval_minutes < 1:
        raise ValueError("expected_interval_minutes must be at least 1")

    frame = candles.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values("timestamp")
    deltas = frame["timestamp"].diff().dropna().dt.total_seconds().div(60)
    interval = float(deltas.median()) if not deltas.empty else None
    duplicates = int(frame["timestamp"].duplicated().sum())
    gaps = int((deltas > expected_interval_minutes).sum())
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
