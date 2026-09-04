"""Deterministic, pseudonymous Maths practice sessions for the V2.5 classroom."""

import secrets
from dataclasses import dataclass
from fractions import Fraction


QUESTION_BANK = {
    "Whole Numbers": {
        "Easy": [
            ("What is 48 + 27?", "Add the tens, then add the ones.", "75", "Step 1: Add the ones: 8 + 7 = 15. Write 5 and carry 1.\nStep 2: Add the tens: 4 + 2 + 1 = 7.\nTherefore, 48 + 27 = 75."),
            ("What is 9 × 7?", "Think of nine groups of seven.", "63", "Step 1: Multiplication means equal groups. Here we have 9 groups of 7.\nStep 2: Add nine sevens, or use the multiplication table: 9 × 7 = 63.\nTherefore, the answer is 63."),
        ],
        "Medium": [
            ("What is 144 ÷ 12?", "Which number multiplied by 12 gives 144?", "12", "Step 1: Division asks how many groups of 12 fit into 144.\nStep 2: Use the inverse operation: 12 × 12 = 144.\nTherefore, 144 ÷ 12 = 12."),
            ("Calculate 325 - 178.", "Borrow carefully from the tens and hundreds columns.", "147", "Step 1: Borrow so the ones become 15 - 8 = 7.\nStep 2: Borrow again so the tens become 11 - 7 = 4.\nStep 3: Subtract the hundreds: 2 - 1 = 1.\nTherefore, 325 - 178 = 147."),
        ],
        "Challenge": [
            ("Calculate (18 × 6) - 35.", "Complete the multiplication before the subtraction.", "73", "Step 1: Follow the order of operations and multiply first: 18 × 6 = 108.\nStep 2: Subtract 35: 108 - 35 = 73.\nTherefore, the answer is 73."),
            ("What is 15² - 49?", "Square 15 first.", "176", "Step 1: 15² means 15 × 15, which is 225.\nStep 2: Subtract 49 from 225: 225 - 49 = 176.\nTherefore, the answer is 176."),
        ],
    },
    "Fractions": {
        "Easy": [
            ("Calculate 1/4 + 2/4.", "The denominators are already the same.", "3/4", "Step 1: The denominators are both 4, so keep the denominator.\nStep 2: Add the numerators: 1 + 2 = 3.\nTherefore, 1/4 + 2/4 = 3/4."),
            ("Simplify 6/12.", "Divide the numerator and denominator by 6.", "1/2", "Step 1: The highest common factor of 6 and 12 is 6.\nStep 2: Divide both parts by 6: 6 ÷ 6 = 1 and 12 ÷ 6 = 2.\nTherefore, 6/12 = 1/2."),
        ],
        "Medium": [
            ("Calculate 2/3 + 1/6.", "Use 6 as the common denominator.", "5/6", "Step 1: Use 6 as the common denominator.\nStep 2: Convert 2/3 to 4/6.\nStep 3: Add: 4/6 + 1/6 = 5/6.\nTherefore, the answer is 5/6."),
            ("Calculate 3/4 - 1/8.", "Rewrite 3/4 with denominator 8.", "5/8", "Step 1: Use 8 as the common denominator.\nStep 2: Convert 3/4 to 6/8.\nStep 3: Subtract: 6/8 - 1/8 = 5/8.\nTherefore, the answer is 5/8."),
        ],
        "Challenge": [
            ("Calculate 5/6 × 9/10. Give the simplest fraction.", "Multiply, then cancel common factors.", "3/4", "Step 1: Multiply the numerators: 5 × 9 = 45.\nStep 2: Multiply the denominators: 6 × 10 = 60.\nStep 3: Divide 45 and 60 by 15.\nTherefore, 45/60 = 3/4."),
            ("Calculate 7/8 ÷ 14/15. Give the simplest fraction.", "Multiply by the reciprocal of 14/15.", "15/16", "Step 1: Change division to multiplication by the reciprocal: 7/8 × 15/14.\nStep 2: Cancel 7 with 14 to get 1/2.\nStep 3: Multiply: 15/(8 × 2) = 15/16.\nTherefore, the answer is 15/16."),
        ],
    },
    "Algebra": {
        "Easy": [
            ("Solve x + 7 = 15.", "Subtract 7 from both sides.", "8", "Step 1: Subtract 7 from both sides.\nStep 2: x = 15 - 7.\nTherefore, x = 8."),
            ("Solve 3x = 21.", "Divide both sides by 3.", "7", "Step 1: 3x means 3 multiplied by x.\nStep 2: Divide both sides by 3: x = 21 ÷ 3.\nTherefore, x = 7."),
        ],
        "Medium": [
            ("Solve 2x + 5 = 19.", "Subtract 5 first, then divide by 2.", "7", "Step 1: Subtract 5 from both sides: 2x = 14.\nStep 2: Divide both sides by 2: x = 14 ÷ 2.\nTherefore, x = 7."),
            ("Solve 5x - 8 = 27.", "Add 8 to both sides first.", "7", "Step 1: Add 8 to both sides: 5x = 35.\nStep 2: Divide both sides by 5: x = 35 ÷ 5.\nTherefore, x = 7."),
        ],
        "Challenge": [
            ("Solve 3(x + 4) = 30.", "Divide by 3 before isolating x.", "6", "Step 1: Divide both sides by 3: x + 4 = 10.\nStep 2: Subtract 4 from both sides: x = 6.\nCheck: 3(6 + 4) = 30. Therefore, x = 6."),
            ("Solve 4x - 7 = 2x + 13.", "Collect the x terms on one side.", "10", "Step 1: Subtract 2x from both sides: 2x - 7 = 13.\nStep 2: Add 7 to both sides: 2x = 20.\nStep 3: Divide by 2. Therefore, x = 10."),
        ],
    },
    "Ratio & Percentage": {
        "Easy": [
            ("What is 25% of 80?", "25% is one quarter.", "20", "Step 1: Convert 25% to 25/100, which simplifies to 1/4.\nStep 2: Find one quarter of 80: 80 ÷ 4 = 20.\nTherefore, 25% of 80 is 20."),
            ("Simplify the ratio 12:18.", "Divide both terms by 6.", "2:3", "Step 1: The highest common factor of 12 and 18 is 6.\nStep 2: Divide both terms by 6: 12 ÷ 6 = 2 and 18 ÷ 6 = 3.\nTherefore, 12:18 simplifies to 2:3."),
        ],
        "Medium": [
            ("Increase 200 by 15%.", "Find 15% of 200, then add it.", "230", "Step 1: Find 15% of 200: 15/100 × 200 = 30.\nStep 2: Add the increase: 200 + 30 = 230.\nTherefore, the new value is 230."),
            ("Share 84 in the ratio 3:4. What is the larger share?", "There are 7 equal parts altogether.", "48", "Step 1: Add the ratio parts: 3 + 4 = 7.\nStep 2: Find one part: 84 ÷ 7 = 12.\nStep 3: The larger share is 4 × 12 = 48.\nTherefore, the larger share is 48."),
        ],
        "Challenge": [
            ("After a 20% discount, an item costs ₦4,800. What was its original price?", "₦4,800 represents 80% of the original price.", "6000", "Step 1: After a 20% discount, 80% remains.\nStep 2: Let the original price be P: 0.8P = 4,800.\nStep 3: P = 4,800 ÷ 0.8 = 6,000.\nTherefore, the original price was ₦6,000."),
            ("A quantity rises from 240 to 300. What is the percentage increase?", "Find the increase, divide by the original, then multiply by 100.", "25", "Step 1: Find the increase: 300 - 240 = 60.\nStep 2: Divide by the original value: 60 ÷ 240 = 0.25.\nStep 3: Convert to a percentage: 0.25 × 100 = 25%.\nTherefore, the increase is 25%."),
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
PRAISE_MESSAGES = (
    "Excellent work! You got it right.",
    "Well done! Your answer is correct.",
    "Great thinking! Keep it up.",
    "Brilliant! You solved that correctly.",
)


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
        "message": secrets.choice(PRAISE_MESSAGES) if correct else "Good attempt. Let’s work through it step by step.",
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
