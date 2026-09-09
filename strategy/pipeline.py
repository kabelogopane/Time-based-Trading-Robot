"""End-to-end research signal pipeline for the time-based model."""

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from strategy.confluence import qualify_confluence
from strategy.displacement import has_displacement
from strategy.fvg import find_fvgs
from strategy.liquidity import find_liquidity_sweeps
from strategy.market_structure import structure_state


@dataclass(frozen=True)
class PipelineSignal:
    direction: str
    entry: float
    entry_timestamp: object
    liquidity_type: str
    structure: str
    fvg_direction: str
    reason: str


def _first_fvg_retest(frame: pd.DataFrame, gap) -> tuple[object, float] | None:
    """Return the first candle after an FVG is formed that trades into its zone."""
    if gap.third_timestamp is None:
        return None

    later = frame[frame["timestamp"] > pd.Timestamp(gap.third_timestamp)]
    for _, row in later.iterrows():
        if float(row["low"]) <= gap.upper and float(row["high"]) >= gap.lower:
            midpoint = (gap.lower + gap.upper) / 2.0
            return row["timestamp"], float(midpoint)
    return None


def scan_execution_window(candles: pd.DataFrame) -> Optional[PipelineSignal]:
    """Find the first fully confirmed research setup in an execution window.

    Confirmation order is deliberately explicit:
    liquidity sweep -> structure -> displacement -> FVG -> FVG retest.
    The entry is the FVG midpoint on the first later candle that trades into
    the gap. The function returns a signal only; it never places orders.
    """
    if candles.empty:
        return None

    frame = candles.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values("timestamp").reset_index(drop=True)

    sweeps = find_liquidity_sweeps(frame)
    fvgs = find_fvgs(frame)

    for sweep in sweeps:
        direction = "long" if sweep.direction == "low" else "short"
        expected_structure = "bullish" if direction == "long" else "bearish"
        after_sweep = frame[frame["timestamp"] > pd.Timestamp(sweep.timestamp)]
        if after_sweep.empty:
            continue

        for index in after_sweep.index:
            row = frame.loc[index]
            structure = structure_state(frame.loc[:index])
            if structure != expected_structure or not has_displacement(row):
                continue

            expected_fvg = "bullish" if direction == "long" else "bearish"
            matching_fvgs = [
                gap for gap in fvgs
                if gap.direction == expected_fvg
                and gap.third_timestamp is not None
                and pd.Timestamp(gap.third_timestamp) >= pd.Timestamp(row["timestamp"])
            ]

            for gap in matching_fvgs:
                retest = _first_fvg_retest(frame, gap)
                if retest is None:
                    continue
                entry_timestamp, entry = retest

                signal = qualify_confluence(
                    direction=direction,
                    liquidity_swept=True,
                    structure=structure,
                    displacement_confirmed=True,
                    fvg_retested=True,
                )
                if signal is not None:
                    return PipelineSignal(
                        direction=direction,
                        entry=entry,
                        entry_timestamp=entry_timestamp,
                        liquidity_type="sell_side" if sweep.direction == "low" else "buy_side",
                        structure=structure,
                        fvg_direction=gap.direction,
                        reason=signal.reason,
                    )

    return None
