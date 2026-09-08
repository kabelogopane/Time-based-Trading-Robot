"""Run 09:45 session diagnostics on historical OHLCV data."""

from __future__ import annotations

import argparse

from data.loader import load_ohlcv_csv
from research.session_diagnostics import diagnose_sessions


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 09:45 session diagnostics")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    parser.add_argument("--output", default="reports/session_diagnostics.csv")
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    diagnostics = diagnose_sessions(candles)
    diagnostics.to_csv(args.output, index=False)

    print("09:45 SESSION DIAGNOSTICS")
    print("Mode: historical research only")
    print(f"Sessions analyzed: {len(diagnostics)}")
    print(f"Output: {args.output}")
    if not diagnostics.empty:
        print()
        print(diagnostics.to_string(index=False, float_format=lambda value: f"{value:.2f}"))


if __name__ == "__main__":
    main()
