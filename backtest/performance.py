"""Performance statistics for backtest results."""

from __future__ import annotations


def summary(results: list) -> dict:
    """Return compact statistics from TradeResult objects."""
    closed = [r for r in results if r.outcome in {"win", "loss"}]
    wins = [r for r in closed if r.outcome == "win"]
    losses = [r for r in closed if r.outcome == "loss"]
    r_total = sum(r.r_multiple for r in closed)
    return {
        "trades": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": (len(wins) / len(closed) * 100) if closed else 0.0,
        "net_r": r_total,
        "average_r": (r_total / len(closed)) if closed else 0.0,
    }
