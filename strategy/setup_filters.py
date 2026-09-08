"""Objective filters for the 09:45 time-based research model.

ICT/SMC concepts are used here only as measurable supporting conditions.
The 09:45 anchor and 45-candle window remain the primary framework.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Sweep:
    direction: str
    index: int
    price: float


@dataclass(frozen=True)
class FairValueGap:
    direction: str
    index: int
    lower: float
    upper: float


def directional_displacement(row: pd.Series, threshold: float = 0.70) -> str | None:
    """Return bullish/bearish when body strength and direction agree."""
    candle_range = float(row["high"]) - float(row["low"])
    if candle_range <= 0:
        return None
    ratio = abs(float(row["close"]) - float(row["open"])) / candle_range
    if ratio < threshold:
        return None
    if float(row["close"]) > float(row["open"]):
        return "bullish"
    if float(row["close"]) < float(row["open"]):
        return "bearish"
    return None


def find_anchor_sweep(window: pd.DataFrame, anchor_high: float, anchor_low: float) -> Sweep | None:
    """Find the first clear sweep of an anchor extreme followed by a reclaim.

    Below-anchor sweep -> bullish reaction. Above-anchor sweep -> bearish reaction.
    The close must reclaim the swept level, avoiding a simple breakout being
    mislabeled as a liquidity sweep.
    """
    for index, row in window.reset_index(drop=True).iterrows():
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        if low < anchor_low and close > anchor_low:
            return Sweep("long", index, low)
        if high > anchor_high and close < anchor_high:
            return Sweep("short", index, high)
    return None


def has_mss(window: pd.DataFrame, start_index: int, direction: str, lookback: int = 3) -> int | None:
    """Find the first close through the recent range after the sweep."""
    frame = window.reset_index(drop=True)
    for index in range(max(start_index + 1, lookback), len(frame)):
        previous = frame.iloc[index - lookback:index]
        close = float(frame.iloc[index]["close"])
        if direction == "long" and close > float(previous["high"].max()):
            return index
        if direction == "short" and close < float(previous["low"].min()):
            return index
    return None


def find_displacement(window: pd.DataFrame, start_index: int, direction: str, threshold: float = 0.70) -> int | None:
    """Find the first directional displacement after a sweep."""
    frame = window.reset_index(drop=True)
    expected = "bullish" if direction == "long" else "bearish"
    for index in range(start_index + 1, len(frame)):
        if directional_displacement(frame.iloc[index], threshold) == expected:
            return index
    return None


def find_fvg(window: pd.DataFrame, start_index: int, direction: str) -> FairValueGap | None:
    """Find the first three-candle fair-value-gap after confirmation."""
    frame = window.reset_index(drop=True)
    for index in range(max(start_index, 2), len(frame)):
        current = frame.iloc[index]
        two_back = frame.iloc[index - 2]
        if direction == "long" and float(current["low"]) > float(two_back["high"]):
            return FairValueGap("long", index, float(two_back["high"]), float(current["low"]))
        if direction == "short" and float(current["high"]) < float(two_back["low"]):
            return FairValueGap("short", index, float(current["high"]), float(two_back["low"]))
    return None


def fvg_retracement_entry(window: pd.DataFrame, fvg: FairValueGap) -> tuple[int, float] | None:
    """Return the first later candle that retraces to the FVG midpoint."""
    frame = window.reset_index(drop=True)
    midpoint = (fvg.lower + fvg.upper) / 2.0
    for index in range(fvg.index + 1, len(frame)):
        row = frame.iloc[index]
        if float(row["low"]) <= midpoint <= float(row["high"]):
            return index, midpoint
    return None
