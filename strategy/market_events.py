"""Deterministic market-event mapping for the original time model.

The module records observable price events around the model checkpoints. Terms
such as liquidity are used as explicit price-range references, not as claims
about a hidden market mechanism.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from strategy.displacement import has_displacement
from strategy.market_structure import classify_structure
from strategy.session_map import LABELS, MODEL_TIMES


@dataclass(frozen=True)
class MarketEvent:
    time: str
    label: str
    liquidity_reference: str
    liquidity_event: str
    break_direction: str
    structure: str
    displacement: bool
    confirmation: str
    status: str


def _latest_at_time(candles: pd.DataFrame, model_time: str) -> pd.Series | None:
    matches = candles[candles["timestamp"].dt.strftime("%H:%M") == model_time]
    if matches.empty:
        return None
    return matches.iloc[-1]


def _liquidity_event(row: pd.Series, anchor_high: float, anchor_low: float) -> tuple[str, str]:
    """Return the observed reference and whether it was exceeded."""
    if float(row["high"]) > anchor_high:
        return "anchor_high", "buy_side_reference_taken"
    if float(row["low"]) < anchor_low:
        return "anchor_low", "sell_side_reference_taken"
    return "anchor_range", "inside_anchor_range"


def build_market_events(candles: pd.DataFrame) -> list[MarketEvent]:
    """Map each model checkpoint to observable price-event fields."""
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    frame = candles.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    anchor = _latest_at_time(frame, "09:45")
    if anchor is None:
        return [
            MarketEvent(
                time=model_time,
                label=LABELS[model_time],
                liquidity_reference="none",
                liquidity_event="none",
                break_direction="none",
                structure="neutral",
                displacement=False,
                confirmation="none",
                status="missing_anchor",
            )
            for model_time in MODEL_TIMES
        ]

    anchor_high = float(anchor["high"])
    anchor_low = float(anchor["low"])
    events: list[MarketEvent] = []

    for model_time in MODEL_TIMES:
        row = _latest_at_time(frame, model_time)
        if row is None:
            events.append(MarketEvent(
                model_time, LABELS[model_time], "none", "none", "none",
                "neutral", False, "none", "missing",
            ))
            continue

        if model_time == "09:45":
            events.append(MarketEvent(
                model_time, LABELS[model_time], "anchor_range", "anchor_set",
                "none", "neutral", False, "none", "observed",
            ))
            continue

        reference, liquidity_event = _liquidity_event(row, anchor_high, anchor_low)
        close = float(row["close"])
        if close > anchor_high:
            break_direction = "bullish"
        elif close < anchor_low:
            break_direction = "bearish"
        else:
            break_direction = "none"

        structure = classify_structure(
            anchor_high,
            anchor_low,
            float(row["high"]),
            float(row["low"]),
        )
        displaced = has_displacement(row)
        confirmed = (
            break_direction == "bullish" and structure == "bullish" and displaced
        ) or (
            break_direction == "bearish" and structure == "bearish" and displaced
        )
        confirmation = break_direction if confirmed else "none"
        events.append(MarketEvent(
            model_time,
            LABELS[model_time],
            reference,
            liquidity_event,
            break_direction,
            structure,
            displaced,
            confirmation,
            "observed",
        ))

    return events


def market_events_frame(candles: pd.DataFrame) -> pd.DataFrame:
    """Return market events as a dashboard-friendly DataFrame."""
    return pd.DataFrame(asdict(event) for event in build_market_events(candles))
