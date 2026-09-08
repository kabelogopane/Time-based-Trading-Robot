"""Session-level diagnostics for the 09:45 New York research model.

This module measures session behaviour without changing trade rules. It is
intended for research, not live trading.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd

from strategy.setup_filters import find_anchor_sweep, find_displacement, has_mss, find_fvg


@dataclass
class SessionDiagnostic:
    date: str
    anchor_high: float
    anchor_low: float
    anchor_range: float
    first_break: str
    first_break_index: int | None
    first_break_distance: float
    sweep_direction: str
    displacement_direction: str
    mss_long: bool
    mss_short: bool
    bullish_fvg: bool
    bearish_fvg: bool
    return_inside_anchor: bool
    move_5: float | None
    move_10: float | None
    move_15: float | None
    move_30: float | None
    move_45: float | None


def _first_break(window: pd.DataFrame, high: float, low: float) -> tuple[str, int | None, float]:
    for i, row in enumerate(window.itertuples(index=False)):
        if row.high > high:
            return "high", i, row.high - high
        if row.low < low:
            return "low", i, low - row.low
    return "none", None, 0.0


def diagnose_sessions(candles: pd.DataFrame) -> pd.DataFrame:
    """Return one diagnostic row per complete 09:45 New York session."""
    rows: list[dict] = []

    if not isinstance(candles.index, pd.DatetimeIndex):
        raise TypeError("candles must use a DatetimeIndex")

    local = candles.copy()
    if local.index.tz is None:
        local.index = local.index.tz_localize("America/New_York")
    else:
        local.index = local.index.tz_convert("America/New_York")

    for date, day in local.groupby(local.index.date):
        anchor = day.between_time("09:45", "09:45")
        if anchor.empty:
            continue
        after = day.between_time("09:46", "10:30")
        if len(after) < 45:
            continue

        anchor_high = float(anchor.high.iloc[0])
        anchor_low = float(anchor.low.iloc[0])
        window = after.iloc[:45].copy()
        first_break, break_index, break_distance = _first_break(window, anchor_high, anchor_low)

        sweep = find_anchor_sweep(window, anchor_high, anchor_low)
        sweep_direction = sweep.direction if sweep else "none"

        displacement = find_displacement(window, 0, sweep_direction or first_break, threshold=0.70)
        displacement_direction = displacement.direction if displacement else "none"

        mss_long = has_mss(window, 0, "long")
        mss_short = has_mss(window, 0, "short")
        bullish_fvg = find_fvg(window, 0, "long") is not None
        bearish_fvg = find_fvg(window, 0, "short") is not None

        return_inside = False
        if break_index is not None:
            for row in window.iloc[break_index + 1 :].itertuples(index=False):
                if row.low <= anchor_high and row.high >= anchor_low:
                    return_inside = True
                    break

        start_close = float(window.close.iloc[0])
        moves = {}
        for n in (5, 10, 15, 30, 45):
            moves[f"move_{n}"] = float(window.close.iloc[n - 1] - start_close) if len(window) >= n else None

        rows.append(asdict(SessionDiagnostic(
            date=str(date),
            anchor_high=anchor_high,
            anchor_low=anchor_low,
            anchor_range=anchor_high - anchor_low,
            first_break=first_break,
            first_break_index=break_index,
            first_break_distance=break_distance,
            sweep_direction=sweep_direction,
            displacement_direction=displacement_direction,
            mss_long=mss_long,
            mss_short=mss_short,
            bullish_fvg=bullish_fvg,
            bearish_fvg=bearish_fvg,
            return_inside_anchor=return_inside,
            **moves,
        )))

    return pd.DataFrame(rows)
