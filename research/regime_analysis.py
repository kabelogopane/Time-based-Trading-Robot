"""Descriptive regime analysis for the 09:45 research model.

This module groups completed session observations by simple, pre-defined
session characteristics. It does not optimize thresholds or select a trading
variant. The purpose is to identify research hypotheses for later out-of-
sample testing.
"""

from __future__ import annotations

import pandas as pd


def _metrics(group: pd.DataFrame) -> dict[str, float | int]:
    closed = group[group["outcome"].isin(["win", "loss"])]
    wins = int((closed["outcome"] == "win").sum())
    losses = int((closed["outcome"] == "loss").sum())
    r = closed["r_multiple"].astype(float)
    gross_profit = float(r[r > 0].sum())
    gross_loss = float(-r[r < 0].sum())
    pf = gross_profit / gross_loss if gross_loss else float("inf") if gross_profit else 0.0
    return {
        "sessions": int(len(group)),
        "closed_trades": int(len(closed)),
        "wins": wins,
        "losses": losses,
        "win_rate": (wins / len(closed) * 100.0) if len(closed) else 0.0,
        "net_r": float(r.sum()) if len(r) else 0.0,
        "average_r": float(r.mean()) if len(r) else 0.0,
        "profit_factor": pf,
    }


def build_regime_report(
    diagnostics: pd.DataFrame,
    observations: pd.DataFrame,
) -> pd.DataFrame:
    """Return descriptive performance by session regime.

    Anchor-range bands use tertiles of the supplied sample only for description;
    they must not be treated as tuned strategy parameters.
    """
    if diagnostics.empty or observations.empty:
        return pd.DataFrame()

    obs = observations.copy()
    if "date" not in obs.columns:
        raise ValueError("observations must contain a date column")

    merged = diagnostics.merge(
        obs[["date", "outcome", "r_multiple"]],
        on="date",
        how="inner",
        validate="one_to_one",
    )
    if merged.empty:
        return pd.DataFrame()

    q1, q2 = merged["anchor_range"].quantile([1 / 3, 2 / 3]).tolist()
    merged["anchor_range_regime"] = pd.cut(
        merged["anchor_range"],
        bins=[float("-inf"), q1, q2, float("inf")],
        labels=["small", "medium", "large"],
        include_lowest=True,
    )

    regimes: list[tuple[str, pd.Series]] = [
        ("first_break_high", merged["first_break"] == "high"),
        ("first_break_low", merged["first_break"] == "low"),
        ("return_inside_true", merged["return_inside_anchor"] == True),
        ("return_inside_false", merged["return_inside_anchor"] == False),
        ("anchor_range_small", merged["anchor_range_regime"] == "small"),
        ("anchor_range_medium", merged["anchor_range_regime"] == "medium"),
        ("anchor_range_large", merged["anchor_range_regime"] == "large"),
    ]

    rows: list[dict] = []
    for name, mask in regimes:
        subset = merged.loc[mask].copy()
        row = {"regime": name, **_metrics(subset)}
        row["avg_anchor_range"] = float(subset["anchor_range"].mean()) if len(subset) else 0.0
        row["avg_move_45"] = float(subset["move_45"].mean()) if len(subset) else 0.0
        rows.append(row)

    return pd.DataFrame(rows)
