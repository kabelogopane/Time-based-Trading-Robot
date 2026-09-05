"""Minimal backtesting engine for the 45-minute time model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from strategy.targets import risk_distance


@dataclass(frozen=True)
class TradeResult:
    direction: str
    entry: float
    invalidation: float
    target: float
    outcome: str
    r_multiple: float


def evaluate_trade(direction: str, entry: float, invalidation: float, target: float, highs: Iterable[float], lows: Iterable[float]) -> TradeResult:
    """Evaluate a hypothetical setup bar-by-bar.

    If stop and target are touched in the same bar, the result is marked
    ambiguous instead of assuming an execution order that the data cannot prove.
    """
    highs = list(map(float, highs))
    lows = list(map(float, lows))
    risk = risk_distance(entry, invalidation)
    if risk == 0:
        raise ValueError("entry and invalidation cannot be equal")

    for high, low in zip(highs, lows):
        if direction == "long":
            hit_stop = low <= invalidation
            hit_target = high >= target
        elif direction == "short":
            hit_stop = high >= invalidation
            hit_target = low <= target
        else:
            raise ValueError("direction must be 'long' or 'short'")

        if hit_stop and hit_target:
            return TradeResult(direction, entry, invalidation, target, "ambiguous", 0.0)
        if hit_stop:
            return TradeResult(direction, entry, invalidation, target, "loss", -1.0)
        if hit_target:
            reward = abs(target - entry)
            return TradeResult(direction, entry, invalidation, target, "win", reward / risk)

    return TradeResult(direction, entry, invalidation, target, "open", 0.0)
