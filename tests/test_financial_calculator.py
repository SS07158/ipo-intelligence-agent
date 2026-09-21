import pytest

from app.tools.financial_calculator import (
    cagr,
    percentage_change,
)


def test_percentage_change():
    result = percentage_change(
        100,
        125,
    )

    assert result == pytest.approx(25.0)


def test_percentage_change_negative():
    result = percentage_change(
        100,
        75,
    )

    assert result == pytest.approx(-25.0)


def test_percentage_change_zero():
    with pytest.raises(ValueError):
        percentage_change(0, 100)


def test_cagr():
    result = cagr(
        100,
        121,
        2,
    )

    assert result == pytest.approx(10.0)


def test_cagr_invalid_start():
    with pytest.raises(ValueError):
        cagr(0, 100, 2)


def test_cagr_invalid_end():
    with pytest.raises(ValueError):
        cagr(100, 0, 2)


def test_cagr_invalid_years():
    with pytest.raises(ValueError):
        cagr(100, 121, 0)