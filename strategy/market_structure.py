"""Market-structure measurements for the time-based research model."""

from __future__ import annotations

import pandas as pd


def classify_structure(
    previous_swing_high: float,
    previous_swing_low: float,
    current_high: float,
    current_low: float,
) -> str:
    """Classify a basic four-point structure as bullish, bearish, or neutral."""
    if current_high > previous_swing_high and current_low > previous_swing_low:
        return "bullish"
    if current_high < previous_swing_high and current_low < previous_swing_low:
        return "bearish"
    return "neutral"


def structure_state(candles: pd.DataFrame, lookback: int = 3) -> str:
    """Return directional structure from the latest completed candles.

    This is deliberately a simple, reproducible proxy. It does not claim to
    identify every ICT swing or market-structure event.
    """
    required = {"high", "low"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if lookback < 1:
        raise ValueError("lookback must be at least 1")
    frame = candles.tail(lookback + 1)
    if len(frame) < lookback + 1:
        return "neutral"
    previous = frame.iloc[:-1]
    current = frame.iloc[-1]
    return classify_structure(
        float(previous["high"].max()),
        float(previous["low"].min()),
        float(current["high"]),
        float(current["low"]),
    )
