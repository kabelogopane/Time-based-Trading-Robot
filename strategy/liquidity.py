"""Liquidity measurements used as supporting evidence."""


def swept_high(previous_high: float, current_high: float, current_close: float) -> bool:
    """Return True when price trades above a prior high but closes back below it."""
    return current_high > previous_high and current_close < previous_high


def swept_low(previous_low: float, current_low: float, current_close: float) -> bool:
    """Return True when price trades below a prior low but closes back above it."""
    return current_low < previous_low and current_close > previous_low
