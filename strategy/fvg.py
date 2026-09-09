"""Fair Value Gap (FVG) detection for the time-based research model.

A three-candle FVG is treated as an objective price-imbalance measurement.
This module does not decide whether an FVG is a valid trade by itself; the
session/entry engine should combine it with the model's time, liquidity,
structure, and displacement rules.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FairValueGap:
    """A detected three-candle fair value gap."""

    direction: str
    lower: float
    upper: float
    first_timestamp: str | None = None
    middle_timestamp: str | None = None
    third_timestamp: str | None = None

    @property
    def size(self) -> float:
        return self.upper - self.lower

    def contains(self, price: float) -> bool:
        """Return True when price is inside the FVG zone."""
        return self.lower <= float(price) <= self.upper


def detect_fvg(first: pd.Series, third: pd.Series, timestamps: tuple[str | None, str | None, str | None] | None = None) -> FairValueGap | None:
    """Detect an FVG using candle 1 and candle 3 of a three-candle sequence.

    Bullish FVG: candle 1 high is below candle 3 low.
    Bearish FVG: candle 1 low is above candle 3 high.
    """
    required = {"high", "low"}
    missing = required.difference(first.index) | required.difference(third.index)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    first_high = float(first["high"])
    first_low = float(first["low"])
    third_high = float(third["high"])
    third_low = float(third["low"])

    ts = timestamps or (None, None, None)

    if first_high < third_low:
        return FairValueGap("bullish", first_high, third_low, *ts)

    if first_low > third_high:
        return FairValueGap("bearish", third_high, first_low, *ts)

    return None


def find_fvgs(candles: pd.DataFrame) -> list[FairValueGap]:
    """Find all three-candle FVGs in chronological OHLC data."""
    required = {"high", "low"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    frame = candles.reset_index(drop=True)
    gaps: list[FairValueGap] = []

    for index in range(len(frame) - 2):
        first = frame.iloc[index]
        middle = frame.iloc[index + 1]
        third = frame.iloc[index + 2]

        timestamps = None
        if "timestamp" in frame.columns:
            timestamps = tuple(
                pd.Timestamp(row["timestamp"]).isoformat()
                for row in (first, middle, third)
            )

        gap = detect_fvg(first, third, timestamps=timestamps)
        if gap is not None:
            gaps.append(gap)

    return gaps


def fvg_retested(gap: FairValueGap, candles: pd.DataFrame) -> bool:
    """Return True when a later candle trades into the FVG zone."""
    required = {"high", "low"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    frame = candles
    if "timestamp" in frame.columns and gap.third_timestamp is not None:
        timestamps = pd.to_datetime(frame["timestamp"])
        frame = frame[timestamps > pd.Timestamp(gap.third_timestamp)]

    return any(
        float(row["low"]) <= gap.upper and float(row["high"]) >= gap.lower
        for _, row in frame.iterrows()
    )
