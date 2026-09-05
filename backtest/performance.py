"""Performance statistics for 45-minute time-model backtests."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime


def _closed(results: Iterable) -> list:
    return [r for r in results if r.outcome in {"win", "loss"}]


def _max_drawdown(r_values: list[float]) -> float:
    """Return maximum peak-to-trough drawdown in R."""
    equity = 0.0
    peak = 0.0
    drawdown = 0.0
    for value in r_values:
        equity += value
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return drawdown


def _streaks(r_values: list[float]) -> tuple[int, int]:
    """Return longest consecutive winning and losing streaks."""
    best_win = best_loss = current_win = current_loss = 0
    for value in r_values:
        if value > 0:
            current_win += 1
            current_loss = 0
            best_win = max(best_win, current_win)
        elif value < 0:
            current_loss += 1
            current_win = 0
            best_loss = max(best_loss, current_loss)
        else:
            current_win = current_loss = 0
    return best_win, best_loss


def summary(results: list) -> dict:
    """Return core statistics from TradeResult/SessionObservation objects."""
    closed = _closed(results)
    wins = [r for r in closed if r.outcome == "win"]
    losses = [r for r in closed if r.outcome == "loss"]
    r_values = [float(r.r_multiple) for r in closed]
    gross_profit = sum(value for value in r_values if value > 0)
    gross_loss = abs(sum(value for value in r_values if value < 0))
    longest_win_streak, longest_loss_streak = _streaks(r_values)

    return {
        "trades": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": (len(wins) / len(closed) * 100) if closed else 0.0,
        "net_r": sum(r_values),
        "average_r": (sum(r_values) / len(closed)) if closed else 0.0,
        "gross_profit_r": gross_profit,
        "gross_loss_r": gross_loss,
        "profit_factor": (gross_profit / gross_loss) if gross_loss else (float("inf") if gross_profit else 0.0),
        "max_drawdown_r": _max_drawdown(r_values),
        "longest_win_streak": longest_win_streak,
        "longest_loss_streak": longest_loss_streak,
        "ambiguous": sum(1 for r in results if r.outcome == "ambiguous"),
        "open": sum(1 for r in results if r.outcome == "open"),
        "no_setup": sum(1 for r in results if r.outcome == "no_setup"),
    }


def by_direction(results: list) -> dict[str, dict]:
    """Calculate the same statistics separately for long and short trades."""
    return {
        direction: summary([r for r in results if r.direction == direction])
        for direction in ("long", "short")
    }


def _entry_window(timestamp: str | None) -> str:
    if not timestamp:
        return "none"
    value = datetime.fromisoformat(timestamp)
    return value.strftime("%H:%M")


def by_entry_window(results: list) -> dict[str, dict]:
    """Group session observations by the candle time that triggered entry."""
    windows: dict[str, list] = {}
    for result in results:
        window = _entry_window(getattr(result, "entry_timestamp", None))
        windows.setdefault(window, []).append(result)
    return {window: summary(items) for window, items in sorted(windows.items())}
