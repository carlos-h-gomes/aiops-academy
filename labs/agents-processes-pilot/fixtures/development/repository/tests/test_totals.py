"""Synthetic tests are inspected as data; this failing fixture is not executed."""

from totals import discounted_total


def test_rounds_final_total_half_up() -> None:
    assert discounted_total(199, 15) == 169


def test_preserves_exact_total() -> None:
    assert discounted_total(200, 15) == 170
