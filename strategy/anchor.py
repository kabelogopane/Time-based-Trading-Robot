"""09:45 anchor calculations.

The anchor is an observation point, not an automatic trade direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class AnchorRange:
    high: float
    low: float

    @property
    def midpoint(self) -> float:
        return (self.high + self.low) / 2

    @property
    def size(self) -> float:
        return self.high - self.low


def build_anchor(high: float, low: float) -> AnchorRange:
    """Create the 09:45 anchor range from validated OHLC data."""
    if high < low:
        raise ValueError("Anchor high cannot be below anchor low")
    return AnchorRange(high=high, low=low)


def detect_anchor(candles: pd.DataFrame, anchor_time: str = "09:45"):
    """Find the configured anchor candle and return its OHLC range.

    This compatibility helper keeps the time-based backtest interface explicit:
    the anchor is the candle stamped at the model's 09:45 checkpoint.
    """
    required = {"timestamp", "high", "low", "close"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    timestamps = pd.to_datetime(candles["timestamp"])
    matches = candles.loc[timestamps.dt.strftime("%H:%M") == anchor_time]
    if matches.empty:
        return None

    row = matches.iloc[0]
    timestamp = pd.Timestamp(row["timestamp"]).to_pydatetime()

    @dataclass(frozen=True)
    class DetectedAnchor:
        timestamp: datetime
        high: float
        low: float
        close: float

    return DetectedAnchor(
        timestamp=timestamp,
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
    )


def price_position(price: float, anchor: AnchorRange) -> str:
    """Classify price relative to the anchor range."""
    if price > anchor.high:
        return "above"
    if price < anchor.low:
        return "below"
    return "inside"
