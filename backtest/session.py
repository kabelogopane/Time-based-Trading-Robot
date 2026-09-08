"""Session runner for the 45-minute time-based research model."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtest.engine import TradeResult, evaluate_trade
from strategy.anchor import detect_anchor
from strategy.candle_windows import forward_candle_window
from strategy.displacement import has_displacement
from strategy.market_structure import classify_structure
from strategy.targets import rr_target

SESSION_START = "08:45"
SESSION_END = "15:45"
CANDLES_PER_WINDOW = 45


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
    first_break_timestamp: str | None = None
    first_break_candles: int | None = None
    returned_inside_anchor: bool = False
    continued_away_from_anchor: bool = False


def _session_slice(candles: pd.DataFrame) -> pd.DataFrame:
    """Keep only the configured New York research session."""
    local = candles.copy()
    local["timestamp"] = pd.to_datetime(local["timestamp"])
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


def _anchor_relative_structure(anchor, row: pd.Series) -> str:
    """Classify the current candle relative to the 09:45 anchor range.

    This is deliberately a simple, reproducible research proxy. It is not a
    full ICT swing-high/swing-low detector.
    """
    return classify_structure(
        float(anchor.high),
        float(anchor.low),
        float(row["high"]),
        float(row["low"]),
    )


def _regime_path_features(post: pd.DataFrame, anchor) -> tuple[str, str | None, int | None, bool, bool]:
    """Measure first-break speed and post-break path without changing entries.

    Speed is measured in candles from the 09:45 anchor to the first close
    outside the anchor. Return/continuation are descriptive labels based on
    subsequent closes and are independent of setup confirmation.
    """
    normalized = post.reset_index(drop=True)
    break_index = None
    first_break = "none"

    for index, row in normalized.iterrows():
        close = float(row["close"])
        if close > anchor.high:
            first_break = "bullish"
            break_index = index
            break
        if close < anchor.low:
            first_break = "bearish"
            break_index = index
            break

    if break_index is None:
        return "none", None, None, False, False

    break_row = normalized.iloc[break_index]
    first_break_timestamp = pd.Timestamp(break_row["timestamp"]).isoformat()
    first_break_candles = break_index + 1
    future = normalized.iloc[break_index + 1 :]
    if future.empty:
        return first_break, first_break_timestamp, first_break_candles, False, False

    closes = future["close"].astype(float)
    if first_break == "bullish":
        returned_inside = bool((closes <= anchor.high).any())
        continued_away = bool((closes > anchor.high).all())
    else:
        returned_inside = bool((closes >= anchor.low).any())
        continued_away = bool((closes < anchor.low).all())

    return first_break, first_break_timestamp, first_break_candles, returned_inside, continued_away


def run_session(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> SessionObservation | None:
    """Analyze one New York session without placing a real order.

    The 09:45 ET candle is the anchor. From that checkpoint, the model now
    examines the next 45 candles as one explicit candle-count window. The
    first close outside the anchor range is recorded once. A setup requires
    anchor-relative structure and candle displacement. This is a testable
    research hypothesis, not a claim about a hidden market algorithm.
    """
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    candles = _session_slice(candles).sort_values("timestamp").reset_index(drop=True)
    anchor = detect_anchor(candles)
    if anchor is None:
        return None

    post = forward_candle_window(candles, pd.Timestamp(anchor.timestamp), CANDLES_PER_WINDOW)
    if post.empty:
        return _empty_observation(anchor, post)

    post_anchor_high = float(post["high"].max())
    post_anchor_low = float(post["low"].min())
    first_break, first_break_timestamp, first_break_candles, returned_inside, continued_away = _regime_path_features(post, anchor)
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

        # Do not allow confirmation on a candle before the first break.
        if first_break_timestamp is None or pd.Timestamp(row["timestamp"]).isoformat() < first_break_timestamp:
            continue

        structure = _anchor_relative_structure(anchor, row)
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
        result = _evaluate_setup(post, entry_timestamp, direction, entry, invalidation, target)
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
        analysis_window_start=post["timestamp"].iloc[0].isoformat(),
        analysis_window_end=post["timestamp"].iloc[-1].isoformat(),
        analysis_candle_count=len(post),
        first_break_timestamp=first_break_timestamp,
        first_break_candles=first_break_candles,
        returned_inside_anchor=returned_inside,
        continued_away_from_anchor=continued_away,
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
