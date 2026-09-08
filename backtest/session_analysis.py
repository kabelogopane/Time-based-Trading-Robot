"""Descriptive analysis of 09:45 sessions.

This module studies which measurable session characteristics are associated with
wins and losses. It does not search parameters for a target win rate and does
not use post-entry information when building setup-time features.
"""

from __future__ import annotations

import pandas as pd

from backtest.session import run_sessions
from strategy.setup_filters import find_anchor_sweep, find_displacement, has_mss


FEATURE_COLUMNS = [
    "anchor_range", "anchor_body", "anchor_body_ratio", "anchor_direction",
    "first_break", "first_break_index", "first_break_distance",
    "sweep_direction", "sweep_index", "sweep_distance",
    "displacement_index", "mss_index", "mss_after_displacement",
]


def _first_break(window: pd.DataFrame, anchor_high: float, anchor_low: float) -> tuple[str, int | None, float | None]:
    for index, row in window.reset_index(drop=True).iterrows():
        close = float(row["close"])
        if close > anchor_high:
            return "bullish", index, close - anchor_high
        if close < anchor_low:
            return "bearish", index, anchor_low - close
    return "none", None, None


def _session_features(day: pd.DataFrame) -> dict | None:
    candles = day.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    candles = candles.sort_values("timestamp").reset_index(drop=True)
    anchors = candles[candles["timestamp"].dt.strftime("%H:%M") == "09:45"]
    if anchors.empty:
        return None
    anchor = anchors.iloc[0]
    window = candles[candles["timestamp"] > anchor["timestamp"]].head(45).reset_index(drop=True)
    if len(window) < 45:
        return None

    ah, al = float(anchor["high"]), float(anchor["low"])
    anchor_range = ah - al
    anchor_body = abs(float(anchor["close"]) - float(anchor["open"]))
    break_direction, break_index, break_distance = _first_break(window, ah, al)

    sweep = find_anchor_sweep(window, ah, al)
    sweep_direction = sweep.direction if sweep else "none"
    sweep_index = sweep.index if sweep else None
    sweep_distance = abs(sweep.price - (al if sweep_direction == "long" else ah)) if sweep else None

    displacement_index = None
    mss_index = None
    mss_after_displacement = None
    if sweep:
        displacement_index = find_displacement(window, sweep.index, sweep.direction)
        mss_index = has_mss(window, sweep.index, sweep.direction)
        if displacement_index is not None and mss_index is not None:
            mss_after_displacement = mss_index >= displacement_index

    return {
        "date": str(pd.Timestamp(anchor["timestamp"]).date()),
        "anchor_range": anchor_range,
        "anchor_body": anchor_body,
        "anchor_body_ratio": anchor_body / anchor_range if anchor_range > 0 else 0.0,
        "anchor_direction": "bullish" if float(anchor["close"]) > float(anchor["open"]) else "bearish" if float(anchor["close"]) < float(anchor["open"]) else "neutral",
        "first_break": break_direction,
        "first_break_index": break_index,
        "first_break_distance": break_distance,
        "sweep_direction": sweep_direction,
        "sweep_index": sweep_index,
        "sweep_distance": sweep_distance,
        "displacement_index": displacement_index,
        "mss_index": mss_index,
        "mss_after_displacement": mss_after_displacement,
    }


def build_session_dataset(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> pd.DataFrame:
    """Build one row per valid 09:45 session with setup-time features and outcome."""
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    features = []
    for _, day in candles.groupby(candles["timestamp"].dt.date):
        row = _session_features(day)
        if row is not None:
            features.append(row)

    result = pd.DataFrame(features)
    observations = run_sessions(candles, reward_to_risk=reward_to_risk)
    outcomes = pd.DataFrame([
        {"date": item.date, "outcome": item.outcome, "r_multiple": item.r_multiple, "entry": item.entry}
        for item in observations
    ])
    if result.empty:
        return result
    return result.merge(outcomes, on="date", how="left")


def compare_feature_groups(dataset: pd.DataFrame) -> pd.DataFrame:
    """Compare win/loss rates for predefined categorical features."""
    if dataset.empty:
        return pd.DataFrame()
    closed = dataset[dataset["outcome"].isin({"win", "loss"})].copy()
    rows: list[dict] = []
    for feature in ["anchor_direction", "first_break", "sweep_direction"]:
        if feature not in closed:
            continue
        for value, group in closed.groupby(feature, dropna=False):
            wins = int((group["outcome"] == "win").sum())
            trades = len(group)
            rows.append({
                "feature": feature,
                "value": value,
                "trades": trades,
                "wins": wins,
                "losses": trades - wins,
                "win_rate": wins / trades * 100 if trades else 0.0,
                "net_r": float(group["r_multiple"].sum()),
                "average_r": float(group["r_multiple"].mean()) if trades else 0.0,
            })
    return pd.DataFrame(rows)
