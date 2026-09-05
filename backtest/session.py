"""Session runner for the 45-minute time-based research model."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtest.engine import TradeResult, evaluate_trade
from strategy.anchor import detect_anchor
from strategy.displacement import has_displacement
from strategy.market_structure import structure_state
from strategy.targets import rr_target

SESSION_START = "08:45"
SESSION_END = "15:45"


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
    outcome: str
    r_multiple: float
    entry_timestamp: str | None


def _session_slice(candles: pd.DataFrame) -> pd.DataFrame:
    """Keep only the configured New York research session."""
    local = candles.copy()
    local["timestamp"] = pd.to_datetime(local["timestamp"])
    times = local["timestamp"].dt.strftime("%H:%M")
    return local[(times >= SESSION_START) & (times <= SESSION_END)].copy()


def _empty_observation(anchor) -> SessionObservation:
    return SessionObservation(
        date=str(anchor.timestamp.date()),
        anchor_high=anchor.high,
        anchor_low=anchor.low,
        anchor_close=anchor.close,
        post_anchor_high=anchor.high,
        post_anchor_low=anchor.low,
        first_break="none",
        first_confirmation="none",
        entry=None,
        invalidation=None,
        target=None,
        outcome="no_setup",
        r_multiple=0.0,
        entry_timestamp=None,
    )


def _evaluate_setup(candles: pd.DataFrame, entry_timestamp: pd.Timestamp, direction: str, entry: float, invalidation: float, target: float) -> TradeResult:
    """Evaluate only candles after the entry candle to avoid same-bar lookahead."""
    future = candles[candles["timestamp"] > entry_timestamp]
    return evaluate_trade(
        direction,
        entry,
        invalidation,
        target,
        highs=future["high"].tolist(),
        lows=future["low"].tolist(),
    )


def run_session(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> SessionObservation | None:
    """Analyze one New York session without placing a real order.

    The 09:45 ET candle is the anchor. The first close outside the anchor
    range is recorded once. A setup requires matching market structure and
    candle displacement. This is a testable research hypothesis, not a claim
    about a hidden market algorithm.
    """
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    candles = _session_slice(candles).sort_values("timestamp").reset_index(drop=True)
    anchor = detect_anchor(candles)
    if anchor is None:
        return None

    post = candles[candles["timestamp"] > pd.Timestamp(anchor.timestamp)].copy()
    if post.empty:
        return _empty_observation(anchor)

    post_anchor_high = float(post["high"].max())
    post_anchor_low = float(post["low"].min())
    first_break = "none"
    first_confirmation = "none"
    entry = invalidation = target = None
    entry_timestamp = None
    outcome = "no_setup"
    r_multiple = 0.0

    for _, row in post.iterrows():
        close = float(row["close"])
        if first_break == "none":
            if close > anchor.high:
                first_break = "bullish"
            elif close < anchor.low:
                first_break = "bearish"
            else:
                continue
        elif first_break not in {"bullish", "bearish"}:
            continue

        history = post[post["timestamp"] <= row["timestamp"]].tail(4)
        structure = structure_state(history, lookback=3)
        displaced = has_displacement(row)
        confirmed = (
            first_break == "bullish" and structure == "bullish" and displaced
        ) or (
            first_break == "bearish" and structure == "bearish" and displaced
        )
        if not confirmed:
            continue

        first_confirmation = first_break
        entry = close
        invalidation = anchor.low if first_break == "bullish" else anchor.high
        direction = "long" if first_break == "bullish" else "short"
        target = rr_target(entry, invalidation, reward_to_risk, direction)
        entry_timestamp = pd.Timestamp(row["timestamp"])
        result = _evaluate_setup(candles, entry_timestamp, direction, entry, invalidation, target)
        outcome = result.outcome
        r_multiple = result.r_multiple
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
        outcome=outcome,
        r_multiple=r_multiple,
        entry_timestamp=entry_timestamp.isoformat() if entry_timestamp is not None else None,
    )


def run_sessions(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> list[SessionObservation]:
    """Run the model independently for every New York calendar date."""
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    observations: list[SessionObservation] = []
    for _, day in candles.groupby(candles["timestamp"].dt.date):
        result = run_session(day, reward_to_risk=reward_to_risk)
        if result is not None:
            observations.append(result)
    return observations
