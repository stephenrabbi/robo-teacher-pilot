"""Check generated linear-equation solutions, operations, and substitution."""

import pytest

import practice_generator as practice


@pytest.mark.parametrize("difficulty,values", [
    ("Easy", (2, 3)), ("Easy", (15, 12)),
    ("Medium", (2, 3, 4)), ("Medium", (12, 7, 15)),
    ("Challenge", (2, 4, 10)), ("Challenge", (15, 6, 2)),
])
def test_algebra_shows_correct_inverse_operations_and_check(monkeypatch, difficulty, values):
    sequence = iter(values)
    monkeypatch.setattr(practice, "_int", lambda lo, hi: next(sequence))
    question, hint, answer, solution = practice.generate_question("Simple Equations", difficulty)
    x = values[0]
    assert answer == str(x)
    assert "Check" in solution
    assert "Both sides are equal" in solution
    assert f"x = {x}" in solution

    if difficulty == "Easy":
        c = values[1]
        total = x + c
        assert question == f"Solve x + {c} = {total}."
        assert f"{x} + {c} = {total}" in solution
        assert total - c == x
    elif difficulty == "Medium":
        a, c = values[1:]
        total = a * x + c
        assert question == f"Solve {a}x + {c} = {total}."
        assert f"{a}({x}) + {c} = {a*x} + {c} = {total}" in solution
        assert (total - c) // a == x
    else:
        a, c = values[1:]
        total = a * (x + c)
        assert question == f"Solve {a}(x + {c}) = {total}."
        assert f"{a}({x} + {c}) = {a} × {x+c} = {total}" in solution
        assert total // a - c == x


@pytest.mark.parametrize("topic", ["Algebra", "Simple Equations"])
def test_algebra_aliases_share_checked_workings(monkeypatch, topic):
    values = iter((8, 4))
    monkeypatch.setattr(practice, "_int", lambda lo, hi: next(values))
    question, hint, answer, solution = practice.generate_question(topic, "Easy")
    assert answer == "8"
    assert "8 + 4 = 12" in solution
