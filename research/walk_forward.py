"""Chronological walk-forward validation for the 09:45 research model.

The validation window is never used to choose the anchor-range threshold. The
threshold is calculated only from the preceding training window and then
frozen for the following validation window.
"""

from __future__ import annotations

import pandas as pd


def _metrics(group: pd.DataFrame) -> dict[str, float | int]:
    closed = group[group["outcome"].isin(["win", "loss"])].copy()
    wins = int((closed["outcome"] == "win").sum())
    losses = int((closed["outcome"] == "loss").sum())
    r = closed["r_multiple"].astype(float)
    gross_profit = float(r[r > 0].sum())
    gross_loss = float(-r[r < 0].sum())
    pf = gross_profit / gross_loss if gross_loss else float("inf") if gross_profit else 0.0
    equity = r.cumsum()
    drawdown = equity.cummax() - equity
    return {
        "sessions": int(len(group)),
        "closed_trades": int(len(closed)),
        "wins": wins,
        "losses": losses,
        "open": int((group["outcome"] == "open").sum()),
        "ambiguous": int((group["outcome"] == "ambiguous").sum()),
        "win_rate": wins / len(closed) * 100.0 if len(closed) else 0.0,
        "net_r": float(r.sum()) if len(r) else 0.0,
        "profit_factor": pf,
        "max_drawdown_r": float(drawdown.max()) if len(drawdown) else 0.0,
    }


def _prepare(diagnostics: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    if diagnostics.empty or observations.empty:
        return pd.DataFrame()
    required_d = {"date", "anchor_range"}
    required_o = {"date", "outcome", "r_multiple"}
    missing_d = required_d - set(diagnostics.columns)
    missing_o = required_o - set(observations.columns)
    if missing_d:
        raise ValueError(f"diagnostics missing columns: {sorted(missing_d)}")
    if missing_o:
        raise ValueError(f"observations missing columns: {sorted(missing_o)}")

    merged = diagnostics.merge(
        observations[["date", "outcome", "r_multiple"]],
        on="date",
        how="inner",
        validate="one_to_one",
    )
    return merged.sort_values("date").reset_index(drop=True)


def walk_forward(
    diagnostics: pd.DataFrame,
    observations: pd.DataFrame,
    train_size: int = 20,
    validation_size: int = 10,
    quantile: float = 2 / 3,
) -> pd.DataFrame:
    """Run rolling chronological validation.

    For each fold, the large-range threshold is the requested quantile of
    anchor ranges in the training window only. The baseline trades every
    validation session; the regime-filtered model trades only sessions at or
    above the frozen threshold.
    """
    data = _prepare(diagnostics, observations)
    if len(data) < train_size + validation_size:
        raise ValueError("not enough complete sessions for the requested walk-forward windows")
    if not 0 < quantile < 1:
        raise ValueError("quantile must be between 0 and 1")

    rows: list[dict] = []
    start = 0
    fold = 1
    while start + train_size + validation_size <= len(data):
        train = data.iloc[start : start + train_size]
        validation = data.iloc[start + train_size : start + train_size + validation_size]
        threshold = float(train["anchor_range"].quantile(quantile))

        for model, subset in (
            ("baseline", validation),
            ("large_range_only", validation[validation["anchor_range"] >= threshold]),
        ):
            metrics = _metrics(subset)
            rows.append({
                "fold": fold,
                "model": model,
                "train_start": str(train["date"].iloc[0]),
                "train_end": str(train["date"].iloc[-1]),
                "validation_start": str(validation["date"].iloc[0]),
                "validation_end": str(validation["date"].iloc[-1]),
                "large_range_threshold": threshold,
                **metrics,
            })

        start += validation_size
        fold += 1

    return pd.DataFrame(rows)
