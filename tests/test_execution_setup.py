import pytest

from strategy.execution_setup import build_execution_setup


def test_builds_long_execution_setup():
    setup = build_execution_setup(
        direction="long",
        entry=110.0,
        invalidation=100.0,
        target=130.0,
        liquidity_swept=True,
        structure="bullish",
        displacement_confirmed=True,
        fvg_retested=True,
    )
    assert setup is not None
    assert setup.direction == "long"
    assert setup.stop == 100.0
    assert setup.target == 130.0
    assert setup.risk_per_unit == 10.0
    assert setup.reward_per_unit == 20.0
    assert setup.rr == 2.0


def test_builds_short_execution_setup():
    setup = build_execution_setup(
        direction="short",
        entry=100.0,
        invalidation=110.0,
        target=80.0,
        liquidity_swept=True,
        structure="bearish",
        displacement_confirmed=True,
        fvg_retested=True,
    )
    assert setup is not None
    assert setup.direction == "short"
    assert setup.rr == 2.0


def test_rejects_setup_without_confluence():
    assert build_execution_setup(
        "long", 110.0, 100.0, 130.0,
        False, "bullish", True, True
    ) is None


def test_rejects_invalid_risk():
    with pytest.raises(ValueError):
        build_execution_setup(
            "long", 100.0, 110.0, 130.0,
            True, "bullish", True, True
        )
