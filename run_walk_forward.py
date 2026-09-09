"""Run chronological walk-forward validation on historical OHLCV data."""

from __future__ import annotations

import argparse

import pandas as pd

from backtest.session import run_sessions
from data.loader import load_ohlcv_csv
from research.session_diagnostics import diagnose_sessions
from research.walk_forward import walk_forward


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 09:45 walk-forward validation")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    parser.add_argument("--rr", type=float, default=2.0)
    parser.add_argument("--train-size", type=int, default=20)
    parser.add_argument("--validation-size", type=int, default=10)
    parser.add_argument("--quantile", type=float, default=2 / 3)
    parser.add_argument("--output", default="reports/walk_forward_results.csv")
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    diagnostics = diagnose_sessions(candles)
    observations = run_sessions(candles, reward_to_risk=args.rr)
    observation_df = pd.DataFrame([vars(item) for item in observations])

    results = walk_forward(
        diagnostics,
        observation_df,
        train_size=args.train_size,
        validation_size=args.validation_size,
        quantile=args.quantile,
    )
    results.to_csv(args.output, index=False)

    print("09:45 WALK-FORWARD VALIDATION")
    print("Mode: historical research only")
    print(f"Sessions available: {len(diagnostics)}")
    print(f"Training window: {args.train_size} sessions")
    print(f"Validation window: {args.validation_size} sessions")
    print(f"Large-range threshold: training {args.quantile:.2%} quantile")
    print(f"Output: {args.output}")
    print()
    print(results.to_string(index=False, float_format=lambda value: f"{value:.2f}"))
    print()
    print("The validation threshold is calculated from training sessions only.")
    print("Results are exploratory because the current dataset contains only 40 complete sessions.")


if __name__ == "__main__":
    main()
