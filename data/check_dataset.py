"""Command-line data quality check for research datasets."""

from __future__ import annotations

import argparse

from data.loader import load_ohlcv_csv
from data.validate import assess_quality


def main() -> None:
    parser = argparse.ArgumentParser(description="Check a historical OHLCV dataset for the 45-candle model")
    parser.add_argument("csv", help="Path to historical OHLCV CSV")
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    quality = assess_quality(candles)
    print("DATA QUALITY CHECK")
    print(f"Rows: {quality.rows}")
    print(f"Median interval: {quality.interval_minutes} minutes")
    print(f"Duplicate timestamps: {quality.duplicate_timestamps}")
    print(f"Gaps: {quality.gaps}")
    print(f"Invalid OHLC rows: {quality.invalid_ohlc}")
    print(f"45-candle model ready: {'YES' if quality.ready_for_45_candle_model else 'NO'}")


if __name__ == "__main__":
    main()
