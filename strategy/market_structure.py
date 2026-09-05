"""Simple, testable market-structure measurements.

These measurements support the time model; they do not replace it.
"""


def classify_structure(previous_swing_high: float, previous_swing_low: float, current_high: float, current_low: float) -> str:
    """Classify a basic four-point structure as bullish, bearish, or neutral."""
    if current_high > previous_swing_high and current_low > previous_swing_low:
        return "bullish"
    if current_high < previous_swing_high and current_low < previous_swing_low:
        return "bearish"
    return "neutral"
