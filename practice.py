"""Deterministic, pseudonymous Maths practice sessions for the V2.5 classroom."""

import secrets
from dataclasses import dataclass
from fractions import Fraction


QUESTION_BANK = {
    "Whole Numbers": {
        "Easy": [
            ("What is 48 + 27?", "Add the tens, then add the ones.", "75", "48 + 27 = 75."),
            ("What is 9 × 7?", "Think of nine groups of seven.", "63", "9 × 7 = 63."),
        ],
        "Medium": [
            ("What is 144 ÷ 12?", "Which number multiplied by 12 gives 144?", "12", "144 ÷ 12 = 12."),
            ("Calculate 325 - 178.", "Borrow carefully from the tens and hundreds columns.", "147", "325 - 178 = 147."),
        ],
        "Challenge": [
            ("Calculate (18 × 6) - 35.", "Complete the multiplication before the subtraction.", "73", "18 × 6 = 108, then 108 - 35 = 73."),
            ("What is 15² - 49?", "Square 15 first.", "176", "15² = 225, then 225 - 49 = 176."),
        ],
    },
    "Fractions": {
        "Easy": [
            ("Calculate 1/4 + 2/4.", "The denominators are already the same.", "3/4", "1/4 + 2/4 = 3/4."),
            ("Simplify 6/12.", "Divide the numerator and denominator by 6.", "1/2", "6/12 = 1/2."),
        ],
        "Medium": [
            ("Calculate 2/3 + 1/6.", "Use 6 as the common denominator.", "5/6", "2/3 = 4/6, so 4/6 + 1/6 = 5/6."),
            ("Calculate 3/4 - 1/8.", "Rewrite 3/4 with denominator 8.", "5/8", "3/4 = 6/8, so 6/8 - 1/8 = 5/8."),
        ],
        "Challenge": [
            ("Calculate 5/6 × 9/10. Give the simplest fraction.", "Multiply, then cancel common factors.", "3/4", "5/6 × 9/10 = 45/60 = 3/4."),
            ("Calculate 7/8 ÷ 14/15. Give the simplest fraction.", "Multiply by the reciprocal of 14/15.", "15/16", "7/8 × 15/14 = 105/112 = 15/16."),
        ],
    },
    "Algebra": {
        "Easy": [
            ("Solve x + 7 = 15.", "Subtract 7 from both sides.", "8", "x = 15 - 7 = 8."),
            ("Solve 3x = 21.", "Divide both sides by 3.", "7", "x = 21 ÷ 3 = 7."),
        ],
        "Medium": [
            ("Solve 2x + 5 = 19.", "Subtract 5 first, then divide by 2.", "7", "2x = 14, so x = 7."),
            ("Solve 5x - 8 = 27.", "Add 8 to both sides first.", "7", "5x = 35, so x = 7."),
        ],
        "Challenge": [
            ("Solve 3(x + 4) = 30.", "Divide by 3 before isolating x.", "6", "x + 4 = 10, so x = 6."),
            ("Solve 4x - 7 = 2x + 13.", "Collect the x terms on one side.", "10", "2x = 20, so x = 10."),
        ],
    },
    "Ratio & Percentage": {
        "Easy": [
            ("What is 25% of 80?", "25% is one quarter.", "20", "One quarter of 80 is 20."),
            ("Simplify the ratio 12:18.", "Divide both terms by 6.", "2:3", "12:18 = 2:3."),
        ],
        "Medium": [
            ("Increase 200 by 15%.", "Find 15% of 200, then add it.", "230", "15% of 200 is 30, so the new value is 230."),
            ("Share 84 in the ratio 3:4. What is the larger share?", "There are 7 equal parts altogether.", "48", "84 ÷ 7 = 12; the larger share is 4 × 12 = 48."),
        ],
        "Challenge": [
            ("After a 20% discount, an item costs ₦4,800. What was its original price?", "₦4,800 represents 80% of the original price.", "6000", "₦4,800 ÷ 0.8 = ₦6,000."),
            ("A quantity rises from 240 to 300. What is the percentage increase?", "Find the increase, divide by the original, then multiply by 100.", "25", "The increase is 60; 60 ÷ 240 × 100 = 25%."),
        ],
    },
}


@dataclass
class PracticeState:
    topic: str
    difficulty: str
    question: str
    hint: str
    expected: str
    explanation: str
    correct: int = 0
    attempted: int = 0
    question_number: int = 1
    answered: bool = False


_sessions: dict[str, PracticeState] = {}


def _choose_question(topic: str, difficulty: str, previous: str = ""):
    choices = QUESTION_BANK[topic][difficulty]
    available = [item for item in choices if item[0] != previous] or choices
    return secrets.choice(available)


def start_practice(student_id: str, topic: str, difficulty: str) -> dict:
    if topic not in QUESTION_BANK or difficulty not in QUESTION_BANK[topic]:
        raise ValueError("Unsupported practice selection")
    question, hint, expected, explanation = _choose_question(topic, difficulty)
    state = PracticeState(topic, difficulty, question, hint, expected, explanation)
    _sessions[student_id] = state
    return _public_question(state)


def _normalise_answer(answer: str) -> str:
    clean = answer.strip().lower().replace(",", "").replace("₦", "").replace("%", "")
    if clean.startswith("x="):
        clean = clean[2:].strip()
    if ":" in clean:
        left, right = clean.split(":", 1)
        ratio = Fraction(int(left.strip()), int(right.strip()))
        return f"{ratio.numerator}:{ratio.denominator}"
    try:
        return str(Fraction(clean))
    except (ValueError, ZeroDivisionError):
        return clean


def answer_practice(student_id: str, answer: str) -> dict:
    state = _sessions.get(student_id)
    if not state:
        raise LookupError("No active practice session")
    if state.answered:
        raise RuntimeError("Question already answered")
    correct = _normalise_answer(answer) == _normalise_answer(state.expected)
    state.attempted += 1
    state.correct += int(correct)
    state.answered = True
    return {
        "correct": correct,
        "expected_answer": state.expected,
        "explanation": state.explanation,
        "score": state.correct,
        "attempted": state.attempted,
        "percentage": round(state.correct / state.attempted * 100),
    }


def next_question(student_id: str) -> dict:
    state = _sessions.get(student_id)
    if not state:
        raise LookupError("No active practice session")
    if not state.answered:
        raise RuntimeError("Answer the current question first")
    question, hint, expected, explanation = _choose_question(state.topic, state.difficulty, state.question)
    state.question, state.hint, state.expected, state.explanation = question, hint, expected, explanation
    state.question_number += 1
    state.answered = False
    return _public_question(state)


def _public_question(state: PracticeState) -> dict:
    return {
        "topic": state.topic,
        "difficulty": state.difficulty,
        "question": state.question,
        "hint": state.hint,
        "question_number": state.question_number,
        "score": state.correct,
        "attempted": state.attempted,
    }
