"""Check numerical accuracy and teaching steps for JSS number bases practice."""

import pytest

import practice_generator as practice


@pytest.mark.parametrize("value", [4, 5, 13, 16, 31])
def test_decimal_to_binary_shows_all_division_steps(monkeypatch, value):
    monkeypatch.setattr(practice, "_int", lambda low, high: value)
    question, hint, answer, explanation = practice.generate_question("Number Bases", "Easy")
    assert question == f"Write {value} in base two."
    assert answer == format(value, "b")
    assert "remainder" in explanation
    dividend = value
    while dividend:
        quotient, remainder = divmod(dividend, 2)
        assert f"{dividend} ÷ 2 = {quotient} remainder {remainder}" in explanation
        dividend = quotient
    assert f"{answer}₂" in explanation


@pytest.mark.parametrize("value", [8, 11, 37, 63])
def test_binary_to_decimal_shows_occupied_place_values(monkeypatch, value):
    monkeypatch.setattr(practice, "_int", lambda low, high: value)
    binary = format(value, "b")
    question, hint, answer, explanation = practice.generate_question("Number Bases", "Medium")
    assert question == f"Convert {binary}₂ to base ten."
    assert int(answer) == value
    assert f"= {value}" in explanation
    for power, bit in enumerate(reversed(binary)):
        if bit == "1":
            assert f"2^{power} ({2**power})" in explanation


@pytest.mark.parametrize("a,b", [(3, 2), (7, 8), (15, 12), (11, 9)])
def test_binary_addition_shows_conversion_and_sum(monkeypatch, a, b):
    integers = iter([a, b])
    monkeypatch.setattr(practice, "_int", lambda low, high: next(integers))
    question, hint, answer, explanation = practice.generate_question("Number Bases", "Challenge")
    assert answer == format(a + b, "b")
    assert f"{format(a, 'b')}₂ + {format(b, 'b')}₂" in question
    assert f"{a} + {b} = {a+b}" in explanation
    dividend = a + b
    while dividend:
        quotient, remainder = divmod(dividend, 2)
        assert f"{dividend} ÷ 2 = {quotient} remainder {remainder}" in explanation
        dividend = quotient
    assert f"{answer}₂" in explanation
