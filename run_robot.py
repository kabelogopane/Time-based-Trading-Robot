"""Command-line research robot for the 45-minute time-based model.

This program only analyzes historical CSV data. It does not connect to a
broker and does not place live orders.
"""

from __future__ import annotations

import argparse

from backtest.filter_comparison import compare_filters
from backtest.journal import write_csv
from backtest.performance import summary
from backtest.regime import all_regime_summaries, build_regime_table
from backtest.session import run_sessions
from data.loader import load_ohlcv_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the 45-minute time-based research robot")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    parser.add_argument("--rr", type=float, default=2.0, help="Research target reward:risk")
    parser.add_argument("--output", default="reports/trade_journal.csv", help="CSV journal output path")
    parser.add_argument(
        "--compare-filters",
        action="store_true",
        help="Compare current rules with progressively stricter setup filters",
    )
    parser.add_argument(
        "--comparison-output",
        default="reports/filter_comparison.csv",
        help="Filter comparison CSV output",
    )
    parser.add_argument(
        "--regime-analysis",
        action="store_true",
        help="Group the same trades by descriptive 09:45 market regimes",
    )
    parser.add_argument(
        "--regime-output",
        default="reports/regime_sessions.csv",
        help="Per-session regime classification CSV output",
    )
    parser.add_argument(
        "--regime-summary-dir",
        default="reports/regimes",
        help="Directory for regime summary CSV files",
    )
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    observations = run_sessions(candles, reward_to_risk=args.rr)
    results = [item for item in observations if item.outcome in {"win", "loss", "ambiguous", "open"}]
    stats = summary(results)
    output = write_csv(observations, args.output)

    print("45-MINUTE TIME-BASED RESEARCH ROBOT")
    print("Mode: historical research / paper simulation only")
    print(f"Sessions analyzed: {len(observations)}")
    print(f"Journal: {output}")
    print()
    print(f"Closed trades: {stats['trades']}")
    print(f"Wins: {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Win rate: {stats['win_rate']:.2f}%")
    print(f"Net R: {stats['net_r']:.2f}")

    if args.compare_filters:
        comparison, _ = compare_filters(candles, reward_to_risk=args.rr)
        comparison.to_csv(args.comparison_output, index=False)
        print()
        print("SETUP FILTER COMPARISON")
        print(comparison.to_string(index=False, float_format=lambda value: f"{value:.2f}"))
        print(f"Comparison: {args.comparison_output}")
        print("No variant is selected by win rate alone; low trade counts require more data.")

    if args.regime_analysis:
        regime_table = build_regime_table(observations)
        regime_table.to_csv(args.regime_output, index=False)
        summaries = all_regime_summaries(observations)
        from pathlib import Path
        summary_dir = Path(args.regime_summary_dir)
        summary_dir.mkdir(parents=True, exist_ok=True)

        print()
        print("STAGE 4 — REGIME ANALYSIS")
        print("Entry, invalidation and 2R target rules are unchanged.")
        for name, table in summaries.items():
            path = summary_dir / f"{name}.csv"
            table.to_csv(path, index=False)
            print()
            print(name.upper())
            if table.empty:
                print("No data")
            else:
                print(table.to_string(index=False, float_format=lambda value: f"{value:.2f}"))
            print(f"Output: {path}")
        print(f"Per-session regimes: {args.regime_output}")

    print()
    for item in observations:
        setup = item.first_confirmation if item.first_confirmation != "none" else "no confirmed setup"
        print(
            f"{item.date} | anchor {item.anchor_high:.2f}/{item.anchor_low:.2f} | "
            f"break={item.first_break} | setup={setup} | "
            f"entry={item.entry if item.entry is not None else '-'} | "
            f"stop={item.invalidation if item.invalidation is not None else '-'} | "
            f"target={item.target if item.target is not None else '-'} | "
            f"outcome={item.outcome} | R={item.r_multiple:.2f}"
        )


if __name__ == "__main__":
    main()
