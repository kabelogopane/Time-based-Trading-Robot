"""Risk controls for research and paper-trading simulations."""

from __future__ import annotations


def risk_amount(balance: float, risk_pct: float) -> float:
    if balance < 0:
        raise ValueError("balance cannot be negative")
    if not 0 <= risk_pct <= 100:
        raise ValueError("risk_pct must be between 0 and 100")
    return balance * risk_pct / 100.0


def position_units(balance: float, risk_pct: float, entry: float, invalidation: float, point_value: float = 1.0) -> float:
    """Return simulated position size from fixed percentage risk."""
    distance = abs(entry - invalidation)
    if distance <= 0 or point_value <= 0:
        raise ValueError("entry/invalidation distance and point_value must be positive")
    return risk_amount(balance, risk_pct) / (distance * point_value)
