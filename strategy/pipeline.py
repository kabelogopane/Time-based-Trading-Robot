"""End-to-end research signal pipeline for the time-based model."""

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from strategy.confluence import qualify_confluence
from strategy.displacement import has_displacement
from strategy.fvg import find_fvgs, fvg_retested
from strategy.liquidity import find_liquidity_sweeps
from strategy.market_structure import structure_state


@dataclass(frozen=True)
class PipelineSignal:
    direction: str
    entry: float
    liquidity_type: str
    structure: str
    fvg_direction: str
    reason: str


def scan_execution_window(candles: pd.DataFrame) -> Optional[PipelineSignal]:
    """Find the first fully confirmed research setup in an execution window.

    The function intentionally returns only a signal. It does not place orders.
    """
    if candles.empty:
        return None

    frame = candles.copy().reset_index(drop=True)
    sweeps = find_liquidity_sweeps(frame)
    fvgs = find_fvgs(frame)

    for sweep in sweeps:
        direction = "long" if sweep.liquidity_type == "sell_side" else "short"
        expected_structure = "bullish" if direction == "long" else "bearish"

        after_sweep = frame[frame["timestamp"] > sweep.timestamp]
        if after_sweep.empty:
            continue

        for index in after_sweep.index:
            row = frame.loc[index]
            structure = structure_state(frame.loc[:index])
            if structure != expected_structure:
                continue
            if not has_displacement(row):
                continue

            matching_fvgs = [
                gap for gap in fvgs
                if gap.direction == ("bullish" if direction == "long" else "bearish")
            ]
            for gap in matching_fvgs:
                if gap.timestamp is not None and pd.Timestamp(gap.timestamp) <= sweep.timestamp:
                    continue
                later = frame[frame["timestamp"] > pd.Timestamp(gap.third_timestamp)]
                if not fvg_retested(gap, later):
                    continue

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
                        entry=float(row["close"]),
                        liquidity_type=sweep.liquidity_type,
                        structure=structure,
                        fvg_direction=gap.direction,
                        reason=signal.reason,
                    )

    return None
