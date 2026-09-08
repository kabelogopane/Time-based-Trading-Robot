"""CLI for discovering 09:45 session characteristics without optimization."""

from __future__ import annotations

import argparse

from data.loader import load_ohlcv_csv
from backtest.session_analysis import build_session_dataset, compare_feature_groups


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze 09:45 session characteristics")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    parser.add_argument("--rr", type=float, default=2.0, help="Research target reward:risk")
    parser.add_argument("--output", default="reports/session_features.csv")
    parser.add_argument("--groups-output", default="reports/session_feature_groups.csv")
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    dataset = build_session_dataset(candles, reward_to_risk=args.rr)
    groups = compare_feature_groups(dataset)
    dataset.to_csv(args.output, index=False)
    groups.to_csv(args.groups_output, index=False)

    closed = dataset[dataset["outcome"].isin({"win", "loss"})]
    print("09:45 SESSION BEHAVIOR ANALYSIS")
    print("Mode: descriptive research; no parameter optimization")
    print(f"Sessions: {len(dataset)}")
    print(f"Closed baseline trades: {len(closed)}")
    print(f"Session features: {args.output}")
    print(f"Feature groups: {args.groups_output}")
    print()
    if not groups.empty:
        print(groups.to_string(index=False, float_format=lambda value: f"{value:.2f}"))
    print()
    print("Use these results to form a small number of pre-declared hypotheses.")
    print("Do not select a rule because it produces the highest win rate on these 40 sessions.")


if __name__ == "__main__":
    main()
