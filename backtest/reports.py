"""Human-readable backtest reporting."""

from __future__ import annotations

from .performance import summary


def text_report(results: list) -> str:
    stats = summary(results)
    return (
        f"Trades: {stats['trades']}\n"
        f"Wins: {stats['wins']}\n"
        f"Losses: {stats['losses']}\n"
        f"Win rate: {stats['win_rate']:.2f}%\n"
        f"Net R: {stats['net_r']:.2f}\n"
        f"Average R: {stats['average_r']:.2f}\n"
    )
