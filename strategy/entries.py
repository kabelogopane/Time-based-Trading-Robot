"""Entry qualification for the time-based model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Setup:
    direction: str
    entry: float
    invalidation: float
    target: float
    reason: str


def qualify_setup(
    direction: str,
    entry: float,
    anchor_high: float,
    anchor_low: float,
    target: float,
    structure: str,
    displacement_confirmed: bool,
) -> Setup | None:
    """Create a hypothetical setup only when objective confirmations agree."""
    if direction not in {"long", "short"}:
        raise ValueError("direction must be 'long' or 'short'")

    expected_structure = "bullish" if direction == "long" else "bearish"
    if structure != expected_structure or not displacement_confirmed:
        return None

    invalidation = anchor_low if direction == "long" else anchor_high
    return Setup(
        direction=direction,
        entry=float(entry),
        invalidation=float(invalidation),
        target=float(target),
        reason="time anchor + structure + displacement confirmation",
    )
