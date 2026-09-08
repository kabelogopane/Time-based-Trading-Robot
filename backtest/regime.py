"""Descriptive regime analysis for the 09:45 research model.

This module does not change setup selection. It groups completed session
observations and reports the same outcomes under different market conditions.
Groups are descriptive, not optimized trading rules.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

import pandas as pd

from backtest.session import SessionObservation

CLOSED_OUTCOMES = {"win", "loss"}


def _outcome_stats(rows: list[SessionObservation]) -> dict[str, float | int]:
    closed = [row for row in rows if row.outcome in CLOSED_OUTCOMES]
    wins = sum(row.outcome == "win" for row in closed)
    losses = sum(row.outcome == "loss" for row in closed)
    net_r = sum(row.r_multiple for row in closed)
    return {
        "sessions": len(rows),
        "closed_trades": len(closed),
        "wins": wins,
        "losses": losses,
        "open": sum(row.outcome == "open" for row in rows),
        "win_rate_pct": round((wins / len(closed) * 100) if closed else 0.0, 2),
        "net_r": round(net_r, 4),
    }


def _range_bucket(value: float, q1: float, q2: float) -> str:
    if value <= q1:
        return "small"
    if value <= q2:
        return "medium"
    return "large"


def build_regime_table(observations: Iterable[SessionObservation]) -> pd.DataFrame:
    """Return one row per session with reproducible regime labels."""
    rows = list(observations)
    if not rows:
        return pd.DataFrame()

    anchor_ranges = [row.anchor_high - row.anchor_low for row in rows]
    q1, q2 = pd.Series(anchor_ranges, dtype=float).quantile([1 / 3, 2 / 3]).tolist()
    records = []
    for row in rows:
        anchor_range = row.anchor_high - row.anchor_low
        if row.first_break_candles is None:
            break_speed = "no_break"
        elif row.first_break_candles <= 5:
            break_speed = "fast"
        elif row.first_break_candles <= 15:
            break_speed = "medium"
        else:
            break_speed = "slow"

        if row.returned_inside_anchor:
            path = "return_inside"
        elif row.continued_away_from_anchor:
            path = "continued_away"
        else:
            path = "mixed"

        data = asdict(row)
        data.update(
            {
                "anchor_range": anchor_range,
                "anchor_range_regime": _range_bucket(anchor_range, q1, q2),
                "break_speed_regime": break_speed,
                "first_break_regime": row.first_break,
                "path_regime": path,
            }
        )
        records.append(data)
    return pd.DataFrame(records)


def summarize_regime(table: pd.DataFrame, column: str) -> pd.DataFrame:
    """Summarize outcomes for one regime column."""
    if table.empty or column not in table.columns:
        return pd.DataFrame()

    output = []
    for value, group in table.groupby(column, dropna=False):
        closed = group[group["outcome"].isin(CLOSED_OUTCOMES)]
        wins = int((closed["outcome"] == "win").sum())
        losses = int((closed["outcome"] == "loss").sum())
        output.append(
            {
                "regime": value,
                "sessions": len(group),
                "closed_trades": len(closed),
                "wins": wins,
                "losses": losses,
                "open": int((group["outcome"] == "open").sum()),
                "win_rate_pct": round((wins / len(closed) * 100) if len(closed) else 0.0, 2),
                "net_r": round(float(closed["r_multiple"].sum()), 4),
                "avg_r": round(float(closed["r_multiple"].mean()), 4) if len(closed) else 0.0,
            }
        )
    return pd.DataFrame(output).sort_values("regime").reset_index(drop=True)


def all_regime_summaries(observations: Iterable[SessionObservation]) -> dict[str, pd.DataFrame]:
    table = build_regime_table(observations)
    return {
        "anchor_range": summarize_regime(table, "anchor_range_regime"),
        "break_speed": summarize_regime(table, "break_speed_regime"),
        "first_break": summarize_regime(table, "first_break_regime"),
        "path": summarize_regime(table, "path_regime"),
    }
