"""Audit observations extracted from the September 2026 trading journal.

These records are manual/paper-trade observations from screenshots, not 1-minute
OHLC candles. They must not be mixed into the robot's candle backtest as if they
were market data.

Research only: no live trading or broker connectivity.
"""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "close_time",
    "instrument",
    "side",
    "close_price",
    "avg_price",
    "units",
    "realized_pnl_usd",
}


def load_september_log(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def summarize_september_log(df: pd.DataFrame) -> dict[str, object]:
    """Summarize visible September paper-trade rows without changing the model."""
    if df.empty:
        return {
            "rows": 0,
            "net_realized_pnl_usd": 0.0,
            "winning_rows": 0,
            "losing_rows": 0,
        }

    pnl = pd.to_numeric(df["realized_pnl_usd"], errors="raise")
    return {
        "rows": int(len(df)),
        "net_realized_pnl_usd": float(pnl.sum()),
        "winning_rows": int((pnl > 0).sum()),
        "losing_rows": int((pnl < 0).sum()),
        "instruments": sorted(df["instrument"].dropna().unique().tolist()),
        "dates": sorted(str(x) for x in df["date"].dropna().unique()),
        "warning": (
            "This is a paper-trade journal audit. It is not a replacement for "
            "September 1-minute OHLC data and must not be used as candle backtest input."
        ),
    }
