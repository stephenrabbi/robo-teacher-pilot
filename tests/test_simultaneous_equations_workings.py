"""Regression tests for both simultaneous-equation elimination patterns."""

import pytest

import practice_generator as practice


@pytest.mark.parametrize("difficulty,values", [
    ("Easy", (2, 5)),
    ("Easy", (15, 1)),
    ("Medium", (3, 14)),
    ("Medium", (11, 11)),
    ("Challenge", (2, 5, 2)),
    ("Challenge", (15, 1, 5)),
    ("Challenge", (4, 12, 3)),
])
def test_simultaneous_equations_show_elimination_substitution_and_checks(
    monkeypatch, difficulty, values
):
    params = iter(values)
    monkeypatch.setattr(practice, "_int", lambda lo, hi: next(params))
    question, hint, answer, steps = practice.generate_question("Simultaneous Equations", difficulty)
    x, y = values[:2]
    assert answer == f"x={x},y={y}"
    assert "eliminate y" in hint
    assert "Substitute" in steps
    assert "Check (1)" in steps and "Check (2)" in steps
    assert "Both equations hold" in steps
    assert f"{x} + {y} = {x+y}" in steps
    if difficulty == "Challenge":
        coefficient = values[2]
        weighted = coefficient*x + y
        assert f"{coefficient}x + y = {weighted}" in question
        assert f"{coefficient}({x}) + {y}" in steps
        assert (coefficient*x + y) == weighted
        assert f"x = {(coefficient-1)*x} ÷ {coefficient-1} = {x}" in steps
    else:
        difference = x-y
        assert f"x - y = {difference}" in question
        assert f"{x} - {y} = {difference}" in steps
        assert f"x = {2*x} ÷ 2 = {x}" in steps


def test_negative_difference_is_presented_with_parentheses(monkeypatch):
    params = iter([3, 12])
    monkeypatch.setattr(practice, "_int", lambda lo, hi: next(params))
    _, _, answer, solution = practice.generate_question("Simultaneous Equations", "Easy")
    assert answer == "x=3,y=12"
    assert "15 + (-9)" in solution
    assert "2x = 6" in solution
