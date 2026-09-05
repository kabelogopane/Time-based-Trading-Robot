"""Generate browser demo data from the authoritative Python research engine."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from backtest.performance import summary
from backtest.session import run_sessions
from data.loader import load_ohlcv_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Export research results for the static web dashboard")
    parser.add_argument("csv", help="Historical OHLCV CSV")
    parser.add_argument("--output", default="app/data/demo-results.json")
    parser.add_argument("--rr", type=float, default=2.0)
    args = parser.parse_args()

    candles = load_ohlcv_csv(args.csv)
    observations = run_sessions(candles, reward_to_risk=args.rr)
    tradable = [o for o in observations if o.outcome in {"win", "loss", "ambiguous", "open"}]

    payload = {
        "generated_by": "Time-Based-Trading-Robot Python research engine",
        "mode": "historical research / paper simulation",
        "live_data": False,
        "broker_connected": False,
        "timezone": "America/New_York",
        "reward_to_risk": args.rr,
        "source_file": str(args.csv),
        "summary": summary(tradable),
        "sessions": [asdict(item) for item in observations],
    }

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
