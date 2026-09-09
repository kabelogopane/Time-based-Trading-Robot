"""Deterministic liquidity-pool and liquidity-sweep helpers for research."""

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class LiquiditySweep:
    """A confirmed sweep of a reference high or low."""

    direction: str
    level: float
    timestamp: Optional[object] = None
    reason: str = ""


def swept_high(previous_high: float, current_high: float, current_close: float) -> bool:
    """Return True when price trades above a prior high but closes back below it."""
    return current_high > previous_high and current_close < previous_high


def swept_low(previous_low: float, current_low: float, current_close: float) -> bool:
    """Return True when price trades below a prior low but closes back above it."""
    return current_low < previous_low and current_close > previous_low


def sweep_high(candle: pd.Series, level: float, timestamp=None) -> Optional[LiquiditySweep]:
    """Detect a buy-side liquidity sweep above a reference high."""
    if candle["high"] > level and candle["close"] < level:
        return LiquiditySweep("high", float(level), timestamp, "high swept and close returned below level")
    return None


def sweep_low(candle: pd.Series, level: float, timestamp=None) -> Optional[LiquiditySweep]:
    """Detect a sell-side liquidity sweep below a reference low."""
    if candle["low"] < level and candle["close"] > level:
        return LiquiditySweep("low", float(level), timestamp, "low swept and close returned above level")
    return None


def find_liquidity_sweeps(candles: pd.DataFrame, lookback: int = 5) -> list[LiquiditySweep]:
    """Find simple local-high/local-low sweeps using a deterministic lookback.

    For each candle, the reference high/low is the highest/lowest value in the
    preceding ``lookback`` completed candles. This is a research proxy for
    nearby liquidity pools and is intentionally not presented as a full ICT
    liquidity model.
    """
    if lookback < 1:
        raise ValueError("lookback must be at least 1")

    required = {"high", "low", "close"}
    missing = required - set(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    sweeps: list[LiquiditySweep] = []
    for i in range(lookback, len(candles)):
        candle = candles.iloc[i]
        previous = candles.iloc[i - lookback:i]
        high_level = float(previous["high"].max())
        low_level = float(previous["low"].min())
        timestamp = candle.get("timestamp")

        high_sweep = sweep_high(candle, high_level, timestamp)
        low_sweep = sweep_low(candle, low_level, timestamp)

        if high_sweep:
            sweeps.append(high_sweep)
        if low_sweep:
            sweeps.append(low_sweep)

    return sweeps
