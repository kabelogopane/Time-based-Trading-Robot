import pandas as pd

from backtest.session_analysis import build_session_dataset, compare_feature_groups


def make_day(direction: str = "bullish") -> pd.DataFrame:
    rows = [{
        "timestamp": "2026-09-01 09:45",
        "open": 102, "high": 105, "low": 100, "close": 104, "volume": 1000,
    }]
    for minute in range(45):
        ts = pd.Timestamp("2026-09-01 10:00") + pd.Timedelta(minutes=minute)
        if direction == "bullish":
            o, h, l, c = 104 + minute, 106 + minute, 103 + minute, 105.5 + minute
        else:
            o, h, l, c = 104 - minute, 105 - minute, 101 - minute, 102.5 - minute
        rows.append({"timestamp": ts, "open": o, "high": h, "low": l, "close": c, "volume": 1000})
    return pd.DataFrame(rows)


def test_build_session_dataset_returns_one_row_with_features():
    dataset = build_session_dataset(make_day())
    assert len(dataset) == 1
    assert dataset.iloc[0]["anchor_range"] == 5
    assert "outcome" in dataset.columns
    assert "first_break" in dataset.columns


def test_feature_group_analysis_is_descriptive():
    dataset = build_session_dataset(make_day())
    groups = compare_feature_groups(dataset)
    assert set(groups["feature"]) == {"anchor_direction", "first_break", "sweep_direction"}
    assert groups["trades"].sum() >= 0
