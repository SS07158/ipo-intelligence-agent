import pytest

from evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_k():
    retrieved = [
        "OUR BUSINESS",
        "INDUSTRY OVERVIEW",
        "INTERNAL RISK",
    ]

    expected = ["INTERNAL RISK"]

    assert recall_at_k(
        retrieved,
        expected,
        3,
    ) == 1.0


def test_recall_miss():
    retrieved = [
        "OUR BUSINESS",
        "INDUSTRY OVERVIEW",
    ]

    expected = ["INTERNAL RISK"]

    assert recall_at_k(
        retrieved,
        expected,
        2,
    ) == 0.0


def test_precision_at_k():
    retrieved = [
        "INTERNAL RISK",
        "OUR BUSINESS",
        "INDUSTRY OVERVIEW",
    ]

    expected = ["INTERNAL RISK"]

    assert precision_at_k(
        retrieved,
        expected,
        3,
    ) == pytest.approx(1 / 3)


def test_reciprocal_rank():
    retrieved = [
        "OUR BUSINESS",
        "INDUSTRY OVERVIEW",
        "INTERNAL RISK",
    ]

    expected = ["INTERNAL RISK"]

    assert reciprocal_rank(
        retrieved,
        expected,
    ) == pytest.approx(1 / 3)