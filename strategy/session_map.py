"""Model-time checkpoints for the original time-based research model."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

MODEL_TIMES = ("08:45", "09:45", "10:45", "11:45", "12:45", "13:45", "15:45")
LABELS = {
    "08:45": "pre_open",
    "09:45": "anchor",
    "10:45": "reaction",
    "11:45": "follow_through",
    "12:45": "midday",
    "13:45": "afternoon",
    "15:45": "pre_close",
}


@dataclass(frozen=True)
class ModelCheckpoint:
    time: str
    label: str
    candle_count: int
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    status: str


def build_session_map(candles: pd.DataFrame) -> list[ModelCheckpoint]:
    """Capture the latest candle at each model time without predicting price."""
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    frame = candles.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values("timestamp")
    result: list[ModelCheckpoint] = []

    for model_time in MODEL_TIMES:
        matches = frame[frame["timestamp"].dt.strftime("%H:%M") == model_time]
        if matches.empty:
            result.append(ModelCheckpoint(model_time, LABELS[model_time], 0, None, None, None, None, "missing"))
            continue
        row = matches.iloc[-1]
        result.append(ModelCheckpoint(
            model_time,
            LABELS[model_time],
            int(len(frame[frame["timestamp"] <= row["timestamp"]])),
            float(row["open"]),
            float(row["high"]),
            float(row["low"]),
            float(row["close"]),
            "observed",
        ))
    return result


def session_map_frame(candles: pd.DataFrame) -> pd.DataFrame:
    """Return checkpoint observations as a dashboard-friendly DataFrame."""
    return pd.DataFrame(asdict(item) for item in build_session_map(candles))
