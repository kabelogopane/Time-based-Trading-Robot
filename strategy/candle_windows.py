"""Candle-count windows for the original time-based research model."""

from __future__ import annotations

import pandas as pd


def forward_candle_window(
    candles: pd.DataFrame,
    start_timestamp: pd.Timestamp,
    candles_per_window: int = 45,
) -> pd.DataFrame:
    """Return the next N candles strictly after a checkpoint.

    This is deliberately candle-count based. With one-minute OHLCV data,
    45 candles represent 45 minutes. With 15-minute data, 45 candles
    represent 11 hours 15 minutes, so the timeframe must always be stated.
    """
    if candles_per_window < 1:
        raise ValueError("candles_per_window must be at least 1")

    frame = candles.copy()
    if "timestamp" not in frame.columns:
        raise ValueError("Missing required column: timestamp")

    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values("timestamp")
    window = frame[frame["timestamp"] > pd.Timestamp(start_timestamp)].head(candles_per_window)
    return window.reset_index(drop=True)
