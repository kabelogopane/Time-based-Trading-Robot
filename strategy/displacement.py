"""Price-displacement measurements."""


def body_size(open_price: float, close: float) -> float:
    return abs(close - open_price)


def displacement(candle) -> float:
    """Measure candle body as a fraction of its total range."""
    high = float(candle["high"])
    low = float(candle["low"])
    open_price = float(candle["open"])
    close = float(candle["close"])
    candle_range = high - low
    if candle_range <= 0:
        return 0.0
    return body_size(open_price, close) / candle_range


def has_displacement(candle, threshold: float = 0.70) -> bool:
    """Return True when the candle body meets the configured strength threshold."""
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    return displacement(candle) >= threshold


def is_bullish_displacement(open_price: float, close: float, average_body: float, multiplier: float = 1.5) -> bool:
    """Objective bullish displacement test."""
    return close > open_price and body_size(open_price, close) >= average_body * multiplier


def is_bearish_displacement(open_price: float, close: float, average_body: float, multiplier: float = 1.5) -> bool:
    """Objective bearish displacement test."""
    return close < open_price and body_size(open_price, close) >= average_body * multiplier
