"""Price-displacement measurements."""


def body_size(open_price: float, close: float) -> float:
    return abs(close - open_price)


def is_bullish_displacement(open_price: float, close: float, average_body: float, multiplier: float = 1.5) -> bool:
    """Objective bullish displacement test."""
    return close > open_price and body_size(open_price, close) >= average_body * multiplier


def is_bearish_displacement(open_price: float, close: float, average_body: float, multiplier: float = 1.5) -> bool:
    """Objective bearish displacement test."""
    return close < open_price and body_size(open_price, close) >= average_body * multiplier
