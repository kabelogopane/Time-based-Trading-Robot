"""Session runner for the 09:45 time-based research model."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from strategy.anchor import detect_anchor
from strategy.displacement import has_displacement
from strategy.market_structure import structure_state
from strategy.targets import rr_target


@dataclass(frozen=True)
class SessionObservation:
    date: str
    anchor_high: float
    anchor_low: float
    anchor_close: float
    post_anchor_high: float
    post_anchor_low: float
    first_break: str
    first_confirmation: str
    entry: float | None
    invalidation: float | None
    target: float | None


def run_session(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> SessionObservation | None:
    """Analyze one trading day without placing a real order.

    A setup is considered only after the 09:45 anchor. The first break is the
    first close outside the anchor range. Structure and candle displacement
    are used as confirmation. This is a research rule, not a claim about a
    hidden market algorithm.
    """
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    candles = candles.sort_values("timestamp").reset_index(drop=True)
    anchor = detect_anchor(candles)
    if anchor is None:
        return None

    post = candles[candles["timestamp"] > pd.Timestamp(anchor.timestamp)].copy()
    if post.empty:
        return SessionObservation(str(anchor.timestamp.date()), anchor.high, anchor.low, anchor.close, anchor.high, anchor.low, "none", "none", None, None, None)

    post_anchor_high = float(post["high"].max())
    post_anchor_low = float(post["low"].min())
    first_break = "none"
    first_confirmation = "none"
    entry = invalidation = target = None

    for index, row in post.iterrows():
        close = float(row["close"])
        if close > anchor.high:
            first_break = "bullish"
        elif close < anchor.low:
            first_break = "bearish"
        else:
            continue

        history = candles[candles["timestamp"] <= row["timestamp"]].tail(4)
        structure = structure_state(history, lookback=3)
        displaced = has_displacement(row)
        if (first_break == "bullish" and structure == "bullish" and displaced) or (first_break == "bearish" and structure == "bearish" and displaced):
            first_confirmation = first_break
            entry = close
            invalidation = anchor.low if first_break == "bullish" else anchor.high
            target = rr_target(entry, invalidation, reward_to_risk, "long" if first_break == "bullish" else "short")
            break

    return SessionObservation(
        date=str(anchor.timestamp.date()),
        anchor_high=anchor.high,
        anchor_low=anchor.low,
        anchor_close=anchor.close,
        post_anchor_high=post_anchor_high,
        post_anchor_low=post_anchor_low,
        first_break=first_break,
        first_confirmation=first_confirmation,
        entry=entry,
        invalidation=invalidation,
        target=target,
    )


def run_sessions(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> list[SessionObservation]:
    """Run the model independently for every date represented in the data."""
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    observations: list[SessionObservation] = []
    for _, day in candles.groupby(candles["timestamp"].dt.date):
        result = run_session(day, reward_to_risk=reward_to_risk)
        if result is not None:
            observations.append(result)
    return observations
