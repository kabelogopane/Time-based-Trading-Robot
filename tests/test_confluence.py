from strategy.confluence import qualify_confluence


def test_long_requires_all_confirmations():
    signal = qualify_confluence(
        "long", True, "bullish", True, True
    )
    assert signal is not None
    assert signal.direction == "long"
    assert "sell-side" in signal.reason


def test_short_requires_all_confirmations():
    signal = qualify_confluence(
        "short", True, "bearish", True, True
    )
    assert signal is not None
    assert signal.direction == "short"
    assert "buy-side" in signal.reason


def test_long_rejects_bearish_structure():
    assert qualify_confluence("long", True, "bearish", True, True) is None


def test_short_rejects_bullish_structure():
    assert qualify_confluence("short", True, "bullish", True, True) is None


def test_missing_confirmation_rejects_setup():
    assert qualify_confluence("long", True, "bullish", False, True) is None
    assert qualify_confluence("long", True, "bullish", True, False) is None
    assert qualify_confluence("long", False, "bullish", True, True) is None
