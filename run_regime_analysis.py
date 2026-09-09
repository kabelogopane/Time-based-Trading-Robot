"""Run descriptive 09:45 regime analysis on historical OHLCV data."""

from __future__ import annotations

import argparse

from data.loader import load_ohlcv_csv
from backtest.session import run_sessions
from research.regime_analysis import build_regime_report
from research.session_diagnostics import diagnose_sessions


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 09:45 regime analysis")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    parser.add_argument("--rr", type=float, default=2.0)
    parser.add_argument("--output", default="reports/regime_analysis.csv")
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    diagnostics = diagnose_sessions(candles)
    observations = run_sessions(candles, reward_to_risk=args.rr)
    observation_df = __import__("pandas").DataFrame([vars(item) for item in observations])
    report = build_regime_report(diagnostics, observation_df)
    report.to_csv(args.output, index=False)

    print("09:45 REGIME ANALYSIS")
    print("Mode: historical research only")
    print(f"Sessions analyzed: {len(diagnostics)}")
    print(f"Output: {args.output}")
    print()
    print(report.to_string(index=False, float_format=lambda value: f"{value:.2f}"))
    print()
    print("Regimes are descriptive hypotheses, not optimized trading rules.")


if __name__ == "__main__":
    main()
