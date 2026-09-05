"""Generate the GitHub Pages dashboard data from the Python research engine."""
from __future__ import annotations

import json
from pathlib import Path

from backtest.performance import summary
from backtest.session import run_sessions
from data.loader import load_ohlcv_csv
from strategy.market_events import market_events_frame


def build_dashboard_payload(source_file: str = "data/sample_45m_sessions.csv", reward_to_risk: float = 2.0) -> dict:
    """Build a JSON-safe dashboard payload from historical OHLCV data."""
    candles = load_ohlcv_csv(source_file)
    observations = run_sessions(candles, reward_to_risk=reward_to_risk)
    results = [
        item for item in observations
        if item.outcome in {"win", "loss", "ambiguous", "open"}
    ]

    sessions = [item.__dict__ for item in observations]
    events = market_events_frame(candles).to_dict(orient="records")

    return {
        "generated_by": "Time-Based-Trading-Robot Python research engine",
        "mode": "historical research / paper simulation",
        "live_data": False,
        "broker_connected": False,
        "timezone": "America/New_York",
        "reward_to_risk": reward_to_risk,
        "source_file": source_file,
        "source_type": "synthetic demo data",
        "summary": summary(results),
        "sessions": sessions,
        "market_events": events,
    }


def export_dashboard(
    output_file: str = "app/data/demo-results.json",
    source_file: str = "data/sample_45m_sessions.csv",
    reward_to_risk: float = 2.0,
) -> Path:
    """Write the dashboard payload as formatted JSON."""
    payload = build_dashboard_payload(source_file, reward_to_risk)
    destination = Path(output_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    return destination


if __name__ == "__main__":
    path = export_dashboard()
    print(f"Dashboard data exported to {path}")
