"""09:45 anchor calculations.

The anchor is an observation point, not an automatic trade direction.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnchorRange:
    high: float
    low: float

    @property
    def midpoint(self) -> float:
        return (self.high + self.low) / 2

    @property
    def size(self) -> float:
        return self.high - self.low


def build_anchor(high: float, low: float) -> AnchorRange:
    """Create the 09:45 anchor range from validated OHLC data."""
    if high < low:
        raise ValueError("Anchor high cannot be below anchor low")
    return AnchorRange(high=high, low=low)


def price_position(price: float, anchor: AnchorRange) -> str:
    """Classify price relative to the anchor range."""
    if price > anchor.high:
        return "above"
    if price < anchor.low:
        return "below"
    return "inside"
