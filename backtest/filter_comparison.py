"""Compare progressively stricter 09:45 setup filters.

The comparison is deliberately descriptive. It does not optimize parameters to
produce a target win rate. All variants use the same 09:45 anchor, 45-candle
window, 2R target, and one-trade-per-session rule.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtest.engine import evaluate_trade
from backtest.session import run_sessions
from strategy.setup_filters import (
    find_anchor_sweep,
    find_displacement,
    find_fvg,
    fvg_retracement_entry,
    has_mss,
)
from strategy.targets import rr_target


VARIANTS = (
    "current",
    "sweep_displacement",
    "sweep_displacement_mss",
    "sweep_displacement_mss_fvg",
    "strict",
)


@dataclass(frozen=True)
class FilterTrade:
    date: str
    variant: str
    direction: str
    entry: float
    invalidation: float
    target: float
    outcome: str
    r_multiple: float
    entry_index: int


def _session_window(frame: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame] | None:
    """Return the 09:45 anchor and the next 45 one-minute candles."""
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    local = candles[candles["timestamp"].dt.strftime("%H:%M").between("09:45", "15:45")]
    local = local.sort_values("timestamp").reset_index(drop=True)
    anchors = local[local["timestamp"].dt.strftime("%H:%M") == "09:45"]
    if anchors.empty:
        return None
    anchor = anchors.iloc[0]
    window = local[local["timestamp"] > anchor["timestamp"]].head(45).reset_index(drop=True)
    if len(window) < 45:
        return None
    return anchor, window


def _enhanced_trade(window: pd.DataFrame, anchor: pd.Series, variant: str, reward_to_risk: float) -> FilterTrade | None:
    ah, al = float(anchor["high"]), float(anchor["low"])
    sweep = find_anchor_sweep(window, ah, al)
    if sweep is None:
        return None

    displacement_index = find_displacement(window, sweep.index, sweep.direction)
    if displacement_index is None:
        return None
    if variant == "sweep_displacement":
        confirmation_index = displacement_index
    else:
        mss_index = has_mss(window, sweep.index, sweep.direction)
        if mss_index is None or displacement_index < mss_index:
            return None
        if variant == "sweep_displacement_mss":
            confirmation_index = mss_index
        else:
            if variant == "strict":
                row = window.iloc[mss_index]
                if sweep.direction == "long" and float(row["close"]) <= ah:
                    return None
                if sweep.direction == "short" and float(row["close"]) >= al:
                    return None

            fvg = find_fvg(window, displacement_index, sweep.direction)
            if fvg is None:
                return None
            retracement = fvg_retracement_entry(window, fvg)
            if retracement is None:
                return None
            entry_index, entry = retracement
            invalidation = sweep.price
            target = rr_target(entry, invalidation, reward_to_risk, sweep.direction)
            future = window.iloc[entry_index + 1 :]
            result = evaluate_trade(
                sweep.direction,
                entry,
                invalidation,
                target,
                future["high"].tolist(),
                future["low"].tolist(),
            )
            return FilterTrade(
                date=str(pd.Timestamp(anchor["timestamp"]).date()),
                variant=variant,
                direction=sweep.direction,
                entry=float(entry),
                invalidation=float(invalidation),
                target=float(target),
                outcome=result.outcome,
                r_multiple=result.r_multiple,
                entry_index=entry_index,
            )

    row = window.iloc[confirmation_index]
    entry = float(row["close"])
    invalidation = sweep.price
    target = rr_target(entry, invalidation, reward_to_risk, sweep.direction)
    future = window.iloc[confirmation_index + 1 :]
    result = evaluate_trade(
        sweep.direction,
        entry,
        invalidation,
        target,
        future["high"].tolist(),
        future["low"].tolist(),
    )
    return FilterTrade(
        date=str(pd.Timestamp(anchor["timestamp"]).date()),
        variant=variant,
        direction=sweep.direction,
        entry=entry,
        invalidation=float(invalidation),
        target=float(target),
        outcome=result.outcome,
        r_multiple=result.r_multiple,
        entry_index=confirmation_index,
    )


def _metrics(trades: list[FilterTrade], session_count: int) -> dict:
    closed = [trade for trade in trades if trade.outcome in {"win", "loss"}]
    values = [float(trade.r_multiple) for trade in closed]
    wins = sum(value > 0 for value in values)
    losses = sum(value < 0 for value in values)
    gross_profit = sum(value for value in values if value > 0)
    gross_loss = abs(sum(value for value in values if value < 0))
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return {
        "sessions": session_count,
        "signals": len(trades),
        "closed_trades": len(closed),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(closed) * 100 if closed else 0.0,
        "net_r": sum(values),
        "average_r": sum(values) / len(closed) if closed else 0.0,
        "profit_factor": gross_profit / gross_loss if gross_loss else (float("inf") if gross_profit else 0.0),
        "max_drawdown_r": max_drawdown,
        "ambiguous": sum(trade.outcome == "ambiguous" for trade in trades),
        "open": sum(trade.outcome == "open" for trade in trades),
    }


def compare_filters(frame: pd.DataFrame, reward_to_risk: float = 2.0) -> tuple[pd.DataFrame, dict[str, list[FilterTrade]]]:
    """Return a side-by-side comparison for the five research variants."""
    candles = frame.copy()
    candles["timestamp"] = pd.to_datetime(candles["timestamp"])
    by_date = [day for _, day in candles.groupby(candles["timestamp"].dt.date)]
    session_count = 0
    all_trades: dict[str, list[FilterTrade]] = {variant: [] for variant in VARIANTS}

    baseline = run_sessions(candles, reward_to_risk=reward_to_risk)
    baseline_by_date = {item.date: item for item in baseline}
    for day in by_date:
        prepared = _session_window(day)
        if prepared is None:
            continue
        session_count += 1
        anchor, window = prepared
        date_key = str(pd.Timestamp(anchor["timestamp"]).date())
        base = baseline_by_date.get(date_key)
        if base is not None and base.outcome in {"win", "loss", "open", "ambiguous"}:
            all_trades["current"].append(
                FilterTrade(
                    date=date_key,
                    variant="current",
                    direction="long" if base.first_confirmation == "bullish" else "short",
                    entry=float(base.entry),
                    invalidation=float(base.invalidation),
                    target=float(base.target),
                    outcome=base.outcome,
                    r_multiple=float(base.r_multiple),
                    entry_index=0,
                )
            )
        for variant in VARIANTS[1:]:
            trade = _enhanced_trade(window, anchor, variant, reward_to_risk)
            if trade is not None:
                all_trades[variant].append(trade)

    rows = []
    for variant in VARIANTS:
        metrics = _metrics(all_trades[variant], session_count)
        metrics["variant"] = variant
        rows.append(metrics)
    return pd.DataFrame(rows), all_trades
