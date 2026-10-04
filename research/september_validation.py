"""September 2026 validation helpers for the time-based research robot.

This module filters a supplied 1-minute OHLCV dataset to September 2026 and
keeps the paper-trade journal separate from candle-based robot results.

Research only: no live trading or broker connectivity.
"""

from __future__ import annotations

import pandas as pd


def september_2026(candles: pd.DataFrame) -> pd.DataFrame:
    """Return only candles whose New York date is in September 2026."""
    frame = candles.copy()
    if "timestamp" not in frame.columns:
        raise ValueError("market data must contain a timestamp column")

    ts = pd.to_datetime(frame["timestamp"], utc=True, errors="raise")
    ny = ts.dt.tz_convert("America/New_York")
    mask = (ny.dt.year == 2026) & (ny.dt.month == 9)
    return frame.loc[mask].copy()


def coverage_report(candles: pd.DataFrame) -> dict[str, object]:
    """Describe September coverage without making assumptions about missing bars."""
    frame = september_2026(candles)
    if frame.empty:
        return {
            "rows": 0,
            "first_timestamp": None,
            "last_timestamp": None,
            "sessions": 0,
        }

    ts = pd.to_datetime(frame["timestamp"], utc=True, errors="raise").dt.tz_convert(
        "America/New_York"
    )
    return {
        "rows": int(len(frame)),
        "first_timestamp": ts.min().isoformat(),
        "last_timestamp": ts.max().isoformat(),
        "sessions": int(ts.dt.date.nunique()),
    }


def compare_journal_dates(
    robot_dates: pd.Series,
    journal_dates: pd.Series,
) -> dict[str, list[str]]:
    """Compare dates present in the robot data and September journal."""
    robot = {str(pd.Timestamp(x).date()) for x in robot_dates.dropna()}
    journal = {str(pd.Timestamp(x).date()) for x in journal_dates.dropna()}
    return {
        "journal_dates_with_robot_data": sorted(robot & journal),
        "journal_dates_missing_from_robot_data": sorted(journal - robot),
        "robot_dates_without_journal_record": sorted(robot - journal),
    }
