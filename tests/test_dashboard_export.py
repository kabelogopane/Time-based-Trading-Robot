import json

from backtest.export_dashboard import build_dashboard_payload, export_dashboard


def test_dashboard_payload_contains_research_metadata_and_events():
    payload = build_dashboard_payload()

    assert payload["mode"] == "historical research / paper simulation"
    assert payload["live_data"] is False
    assert payload["broker_connected"] is False
    assert payload["source_type"] == "synthetic demo data"
    assert len(payload["sessions"]) == 3
    assert len(payload["market_events"]) == 7
    assert payload["market_events"][1]["time"] == "09:45"
    assert payload["market_events"][1]["liquidity_event"] == "anchor_set"


def test_export_writes_valid_json(tmp_path):
    destination = tmp_path / "demo-results.json"
    path = export_dashboard(output_file=destination)

    assert path == destination
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert "summary" in payload
    assert "sessions" in payload
    assert "market_events" in payload
