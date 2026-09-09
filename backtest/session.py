"""Session runner for the 45-minute time-based research model."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtest.engine import TradeResult, evaluate_trade
from strategy.anchor import detect_anchor
from strategy.candle_windows import forward_candle_window
from strategy.pipeline import scan_execution_window
from strategy.targets import rr_target
from strategy.timeframe import aggregate_to_3m, aggregate_to_45m, normalize_new_york

SESSION_START = "08:45"
SESSION_END = "15:45"
EXECUTION_CANDLES_PER_WINDOW = 15


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
    analysis_window_start: str | None
    analysis_window_end: str | None
    analysis_candle_count: int


def _session_slice(candles: pd.DataFrame) -> pd.DataFrame:
    """Keep only the configured New York research session."""
    local = normalize_new_york(candles)
    times = local["timestamp"].dt.strftime("%H:%M")
    return local[(times >= SESSION_START) & (times <= SESSION_END)].copy()


def _empty_observation(anchor, window: pd.DataFrame) -> SessionObservation:
    return SessionObservation(
        date=str(anchor.timestamp.date()),
        anchor_high=anchor.high,
        anchor_low=anchor.low,
        anchor_close=anchor.close,
        post_anchor_high=float(window["high"].max()) if not window.empty else anchor.high,
        post_anchor_low=float(window["low"].min()) if not window.empty else anchor.low,
        first_break="none",
        first_confirmation="none",
        entry=None,
        invalidation=None,
        target=None,
        outcome="no_setup",
        r_multiple=0.0,
        entry_timestamp=None,
        analysis_window_start=(window["timestamp"].iloc[0].isoformat() if not window.empty else None),
        analysis_window_end=(window["timestamp"].iloc[-1].isoformat() if not window.empty else None),
        analysis_candle_count=len(window),
    )


def _evaluate_setup(window: pd.DataFrame, entry_timestamp: pd.Timestamp, direction: str, entry: float, invalidation: float, target: float) -> TradeResult:
    """Evaluate only candles after the entry candle inside the model window."""
    future = window[window["timestamp"] > entry_timestamp]
    return evaluate_trade(
        direction,
        entry,
        invalidation,
        target,
        highs=future["high"].tolist(),
        lows=future["low"].tolist(),
    )


def _prepare_execution_data(candles: pd.DataFrame) -> pd.DataFrame:
    """Return 3-minute execution candles without double-aggregating 3m input."""
    frame = normalize_new_york(candles)
    if len(frame) < 2:
        return frame
    deltas = frame["timestamp"].diff().dropna().dt.total_seconds() / 60
    median_minutes = float(deltas.median())
    if median_minutes <= 1.5:
        return aggregate_to_3m(frame)
    return frame


def run_session(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> SessionObservation | None:
    """Analyze one New York session using a 45m anchor and 3m execution data."""
    raw = _session_slice(frame).sort_values("timestamp").reset_index(drop=True)
    if raw.empty:
        return None

    anchor_data = aggregate_to_45m(raw)
    anchor = detect_anchor(anchor_data)
    if anchor is None:
        return None

    execution = _prepare_execution_data(raw)
    post = forward_candle_window(execution, pd.Timestamp(anchor.timestamp), EXECUTION_CANDLES_PER_WINDOW)
    if post.empty:
        return _empty_observation(anchor, post)

    post_anchor_high = float(post["high"].max())
    post_anchor_low = float(post["low"].min())
    first_break = "none"
    if (post["close"] > anchor.high).any():
        first_break = "bullish"
    elif (post["close"] < anchor.low).any():
        first_break = "bearish"

    signal = scan_execution_window(post)
    entry = invalidation = target = None
    entry_timestamp = None
    outcome = "no_setup"
    r_multiple = 0.0
    first_confirmation = "none"

    if signal is not None:
        first_confirmation = signal.direction
        entry = signal.entry
        direction = signal.direction
        invalidation = anchor.low if direction == "long" else anchor.high
        target = rr_target(entry, invalidation, reward_to_risk, direction)
        entry_timestamp = pd.Timestamp(signal.entry_timestamp)
        result = _evaluate_setup(post, entry_timestamp, direction, entry, invalidation, target)
        outcome = result.outcome
        r_multiple = result.r_multiple

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
        analysis_window_start=post["timestamp"].iloc[0].isoformat(),
        analysis_window_end=post["timestamp"].iloc[-1].isoformat(),
        analysis_candle_count=len(post),
    )


def run_sessions(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> list[SessionObservation]:
    """Run the model independently for every New York calendar date."""
    candles = normalize_new_york(frame)
    observations: list[SessionObservation] = []
    for _, day in candles.groupby(candles["timestamp"].dt.date):
        result = run_session(day, reward_to_risk=reward_to_risk)
        if result is not None:
            observations.append(result)
    return observations
