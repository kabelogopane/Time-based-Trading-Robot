"""Build consecutive 45-minute observations from the 09:45 anchor.

This module measures time first. It does not create live orders or trading
signals. Price, liquidity, displacement, and structure are stored as separate
measurements so the original time model remains the primary framework.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import pandas as pd


@dataclass(frozen=True)
class TimeWindowObservation:
    date: str
    window_start: str
    window_end: str
    candles: int
    open: float
    high: float
    low: float
    close: float
    range: float
    direction: str


def _direction(open_price: float, close: float) -> str:
    if close > open_price:
        return "bullish"
    if close < open_price:
        return "bearish"
    return "neutral"


def build_45m_windows(
    candles: pd.DataFrame,
    anchor_time: str = "09:45",
    interval_minutes: int = 45,
    session_end: str = "15:45",
) -> list[TimeWindowObservation]:
    """Create non-overlapping 45-minute windows after each day's anchor.

    Windows use [start, end) boundaries, so a candle exactly at the next
    boundary belongs to the next window. The anchor candle at 09:45 is part
    of the first window.
    """
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required - set(candles.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be positive")

    frame = candles.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")
    if frame["timestamp"].dt.tz is None:
        frame["timestamp"] = frame["timestamp"].dt.tz_localize("America/New_York")
    else:
        frame["timestamp"] = frame["timestamp"].dt.tz_convert("America/New_York")
    frame = frame.sort_values("timestamp").reset_index(drop=True)

    anchor_hour, anchor_minute = map(int, anchor_time.split(":"))
    end_hour, end_minute = map(int, session_end.split(":"))
    results: list[TimeWindowObservation] = []

    for date, day in frame.groupby(frame["timestamp"].dt.date, sort=True):
        day = day.sort_values("timestamp")
        anchor = pd.Timestamp(date).tz_localize("America/New_York") + pd.Timedelta(
            hours=anchor_hour, minutes=anchor_minute
        )
        session_end_ts = pd.Timestamp(date).tz_localize("America/New_York") + pd.Timedelta(
            hours=end_hour, minutes=end_minute
        )

        start = anchor
        while start < session_end_ts:
            end = min(start + timedelta(minutes=interval_minutes), session_end_ts.to_pydatetime())
            end = pd.Timestamp(end)
            window = day[(day["timestamp"] >= start) & (day["timestamp"] < end)]

            if not window.empty:
                open_price = float(window.iloc[0]["open"])
                high = float(window["high"].max())
                low = float(window["low"].min())
                close = float(window.iloc[-1]["close"])
                results.append(
                    TimeWindowObservation(
                        date=str(date),
                        window_start=start.strftime("%H:%M"),
                        window_end=end.strftime("%H:%M"),
                        candles=len(window),
                        open=open_price,
                        high=high,
                        low=low,
                        close=close,
                        range=high - low,
                        direction=_direction(open_price, close),
                    )
                )
            start = end

    return results
