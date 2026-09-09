"""Build an execution setup after the model confirmations are complete."""

from dataclasses import dataclass
from typing import Optional

from strategy.confluence import qualify_confluence


@dataclass(frozen=True)
class ExecutionSetup:
    """Research-only execution plan."""

    direction: str
    entry: float
    stop: float
    target: float
    risk_per_unit: float
    reward_per_unit: float
    rr: float
    reason: str


def build_execution_setup(
    direction: str,
    entry: float,
    invalidation: float,
    target: float,
    liquidity_swept: bool,
    structure: str,
    displacement_confirmed: bool,
    fvg_retested: bool,
) -> Optional[ExecutionSetup]:
    """Return an execution plan only after full confluence is confirmed."""
    signal = qualify_confluence(
        direction=direction,
        liquidity_swept=liquidity_swept,
        structure=structure,
        displacement_confirmed=displacement_confirmed,
        fvg_retested=fvg_retested,
    )
    if signal is None:
        return None

    if entry <= 0:
        raise ValueError("entry must be positive")

    if direction == "long":
        risk = entry - invalidation
        reward = target - entry
    else:
        risk = invalidation - entry
        reward = entry - target

    if risk <= 0:
        raise ValueError("invalidation must create positive risk")
    if reward <= 0:
        raise ValueError("target must create positive reward")

    return ExecutionSetup(
        direction=direction,
        entry=entry,
        stop=invalidation,
        target=target,
        risk_per_unit=risk,
        reward_per_unit=reward,
        rr=reward / risk,
        reason=signal.reason,
    )
