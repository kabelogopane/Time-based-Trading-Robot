"""Combine the model's objective confirmations into one research signal."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ConfluenceSignal:
    """A fully confirmed research setup."""

    direction: str
    reason: str


def qualify_confluence(
    direction: str,
    liquidity_swept: bool,
    structure: str,
    displacement_confirmed: bool,
    fvg_retested: bool,
) -> Optional[ConfluenceSignal]:
    """Return a signal only when all required confirmations agree.

    Longs require a sell-side liquidity sweep and bullish structure.
    Shorts require a buy-side liquidity sweep and bearish structure.
    Both require displacement and an FVG retest.
    """
    if direction not in {"long", "short"}:
        raise ValueError("direction must be 'long' or 'short'")

    expected_structure = "bullish" if direction == "long" else "bearish"

    if not liquidity_swept:
        return None
    if structure != expected_structure:
        return None
    if not displacement_confirmed:
        return None
    if not fvg_retested:
        return None

    sweep_name = "sell-side" if direction == "long" else "buy-side"
    return ConfluenceSignal(
        direction=direction,
        reason=(
            f"{sweep_name} liquidity sweep + {expected_structure} structure + "
            "displacement + FVG retest"
        ),
    )
