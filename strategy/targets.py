"""Target selection helpers."""

from __future__ import annotations


def risk_distance(entry: float, invalidation: float) -> float:
    return abs(entry - invalidation)


def rr_target(entry: float, invalidation: float, reward_to_risk: float = 2.0, direction: str = "long") -> float:
    """Calculate a hypothetical target from fixed reward:risk."""
    if reward_to_risk <= 0:
        raise ValueError("reward_to_risk must be positive")
    risk = risk_distance(entry, invalidation)
    if risk == 0:
        raise ValueError("entry and invalidation cannot be equal")
    if direction == "long":
        return entry + risk * reward_to_risk
    if direction == "short":
        return entry - risk * reward_to_risk
    raise ValueError("direction must be 'long' or 'short'")
