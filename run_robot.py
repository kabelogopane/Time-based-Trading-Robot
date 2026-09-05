"""Command-line research robot for the 45-minute time-based model.

This program only analyzes historical CSV data. It does not connect to a
broker and does not place live orders.
"""

from __future__ import annotations

import argparse

from backtest.session import run_sessions
from data.loader import load_ohlcv_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the 45-minute time-based research robot")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    parser.add_argument("--rr", type=float, default=2.0, help="Research target reward:risk")
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    observations = run_sessions(candles, reward_to_risk=args.rr)

    print("45-MINUTE TIME-BASED RESEARCH ROBOT")
    print("Mode: historical research / paper simulation only")
    print(f"Sessions analyzed: {len(observations)}")
    print()
    for item in observations:
        setup = item.first_confirmation if item.first_confirmation != "none" else "no confirmed setup"
        print(
            f"{item.date} | anchor {item.anchor_high:.2f}/{item.anchor_low:.2f} | "
            f"break={item.first_break} | setup={setup} | "
            f"entry={item.entry if item.entry is not None else '-'} | "
            f"stop={item.invalidation if item.invalidation is not None else '-'} | "
            f"target={item.target if item.target is not None else '-'}"
        )


if __name__ == "__main__":
    main()
