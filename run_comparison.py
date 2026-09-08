"""Compare progressively stricter versions of the 09:45 research model."""

from __future__ import annotations

import argparse
from pathlib import Path

from backtest.filter_comparison import compare_filters
from data.loader import load_ohlcv_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare 09:45 setup-quality filters")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    parser.add_argument("--rr", type=float, default=2.0, help="Research target reward:risk")
    parser.add_argument("--output", default="reports/filter_comparison.csv", help="Comparison CSV output")
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    comparison, _ = compare_filters(candles, reward_to_risk=args.rr)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(destination, index=False)

    print("09:45 SETUP FILTER COMPARISON")
    print("Mode: historical research / paper simulation only")
    print()
    print(comparison.to_string(index=False, float_format=lambda value: f"{value:.2f}"))
    print()
    print(f"Saved: {destination}")
    print("Note: no variant is declared 'best' from win rate alone. Low trade counts are flagged for research caution.")


if __name__ == "__main__":
    main()
