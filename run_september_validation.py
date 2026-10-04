"""Run the historical robot on September 2026 data only."""

from __future__ import annotations

import argparse

from backtest.performance import summary
from backtest.session import run_sessions
from data.loader import load_ohlcv_csv
from research.september_validation import coverage_report, september_2026


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the 45-minute research robot on September 2026 only"
    )
    parser.add_argument("csv", help="Path to 1-minute OHLCV CSV")
    parser.add_argument("--rr", type=float, default=2.0)
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    september = september_2026(candles)
    coverage = coverage_report(candles)

    observations = run_sessions(september, reward_to_risk=args.rr)
    results = [
        item
        for item in observations
        if item.outcome in {"win", "loss", "ambiguous", "open"}
    ]
    stats = summary(results)

    print("SEPTEMBER 2026 VALIDATION")
    print("Mode: historical research / paper simulation only")
    print(f"Rows: {coverage['rows']}")
    print(f"First NY timestamp: {coverage['first_timestamp']}")
    print(f"Last NY timestamp: {coverage['last_timestamp']}")
    print(f"Sessions: {coverage['sessions']}")
    print()
    print(f"Closed trades: {stats['trades']}")
    print(f"Wins: {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Win rate: {stats['win_rate']:.2f}%")
    print(f"Net R: {stats['net_r']:.2f}")


if __name__ == "__main__":
    main()
