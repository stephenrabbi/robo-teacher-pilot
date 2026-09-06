"""Deterministic, pseudonymous Junior Secondary Maths practice sessions."""

import secrets
from dataclasses import dataclass, field
from fractions import Fraction

from practice_generator import generate_question
from practice_translation import PRACTICE_TEXT, translate_question_batch
from curriculum import CLASS_TOPICS


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
    "Factors, Multiples & Roots": {
        "Easy": [
            ("Find the HCF of 12 and 18.", "List the factors common to both numbers.", "6", "Step 1: Factors of 12 are 1, 2, 3, 4, 6, 12.\nStep 2: Factors of 18 are 1, 2, 3, 6, 9, 18.\nThe highest common factor is 6."),
            ("What is the square root of 81?", "Find the number that multiplies by itself to give 81.", "9", "Step 1: 9 × 9 = 81.\nTherefore, √81 = 9."),
        ],
        "Medium": [
            ("Find the LCM of 8 and 12.", "Write the multiples until you find the first common one.", "24", "Step 1: Multiples of 8 are 8, 16, 24.\nStep 2: Multiples of 12 are 12, 24.\nThe lowest common multiple is 24."),
            ("Express 84 as a product of prime factors.", "Divide repeatedly by the smallest prime numbers.", "2*2*3*7", "Step 1: 84 ÷ 2 = 42 and 42 ÷ 2 = 21.\nStep 2: 21 = 3 × 7.\nTherefore, 84 = 2 × 2 × 3 × 7."),
        ],
        "Challenge": [
            ("Find the smallest number divisible by 6, 8 and 15.", "This is an LCM question.", "120", "Step 1: 6 = 2 × 3, 8 = 2³, and 15 = 3 × 5.\nStep 2: Use the highest powers: 2³ × 3 × 5 = 120.\nTherefore, the LCM is 120."),
            ("What is √196 + √64?", "Find each square root before adding.", "22", "Step 1: √196 = 14.\nStep 2: √64 = 8.\nTherefore, 14 + 8 = 22."),
        ],
    },
    "Decimals & Approximation": {
        "Easy": [
            ("Round 47.68 to the nearest whole number.", "Look at the tenths digit.", "48", "Step 1: The tenths digit is 6.\nStep 2: Since 6 is at least 5, round 47 up.\nTherefore, 47.68 rounds to 48."),
            ("Calculate 3.5 + 2.47.", "Align the decimal points.", "5.97", "Step 1: Write 3.50 + 2.47.\nStep 2: Add each place value.\nTherefore, the sum is 5.97."),
        ],
        "Medium": [
            ("Round 8.746 to 2 decimal places.", "Check the third decimal digit.", "8.75", "Step 1: The hundredths digit is 4 and the next digit is 6.\nStep 2: Round the 4 up to 5.\nTherefore, 8.746 becomes 8.75."),
            ("Write 0.00072 in standard form.", "Move the decimal point until the first number is between 1 and 10.", "7.2*10^-4", "Step 1: Move the decimal point 4 places right to get 7.2.\nStep 2: A rightward move gives a negative power.\nTherefore, 0.00072 = 7.2 × 10⁻⁴."),
        ],
        "Challenge": [
            ("Estimate 19.8 × 5.1 by rounding each number to 1 significant figure.", "Round first, then multiply.", "100", "Step 1: 19.8 rounds to 20.\nStep 2: 5.1 rounds to 5.\nTherefore, the estimate is 20 × 5 = 100."),
            ("Calculate 4.56 ÷ 0.12.", "Multiply both numbers by 100 to remove decimals.", "38", "Step 1: 4.56 ÷ 0.12 = 456 ÷ 12.\nStep 2: 456 ÷ 12 = 38.\nTherefore, the answer is 38."),
        ],
    },
    "Directed Numbers": {
        "Easy": [
            ("Calculate -6 + 9.", "Move 9 steps right from -6 on a number line.", "3", "Step 1: Start at -6.\nStep 2: Moving 9 places right reaches 3.\nTherefore, -6 + 9 = 3."),
            ("Calculate 5 - 12.", "Subtracting 12 means moving left.", "-7", "Step 1: Start at 5.\nStep 2: Move 12 places left.\nTherefore, 5 - 12 = -7."),
        ],
        "Medium": [
            ("Calculate (-7) × 6.", "A negative times a positive is negative.", "-42", "Step 1: 7 × 6 = 42.\nStep 2: The signs are different, so the result is negative.\nTherefore, (-7) × 6 = -42."),
            ("Calculate (-48) ÷ (-8).", "Dividing numbers with the same sign gives a positive result.", "6", "Step 1: 48 ÷ 8 = 6.\nStep 2: Both signs are negative, so the result is positive.\nTherefore, the answer is 6."),
        ],
        "Challenge": [
            ("Calculate -4 × (7 - 10).", "Work inside the brackets first.", "12", "Step 1: 7 - 10 = -3.\nStep 2: -4 × -3 = 12 because two negative signs give a positive result.\nTherefore, the answer is 12."),
            ("Calculate (-36 ÷ 6) - (-8).", "Complete the division before subtraction.", "2", "Step 1: -36 ÷ 6 = -6.\nStep 2: -6 - (-8) = -6 + 8.\nTherefore, the answer is 2."),
        ],
    },
    "Commercial Arithmetic": {
        "Easy": [
            ("A trader buys an item for ₦800 and sells it for ₦950. Find the profit.", "Profit equals selling price minus cost price.", "150", "Step 1: Profit = selling price - cost price.\nStep 2: ₦950 - ₦800 = ₦150.\nTherefore, the profit is ₦150."),
            ("Find the simple interest on ₦2,000 at 5% per year for 1 year.", "Use I = PRT/100.", "100", "Step 1: I = 2,000 × 5 × 1 ÷ 100.\nStep 2: I = 100.\nTherefore, the interest is ₦100."),
        ],
        "Medium": [
            ("An item costing ₦4,000 is sold at a 15% profit. Find the selling price.", "Find the profit, then add it to the cost price.", "4600", "Step 1: 15% of ₦4,000 = ₦600.\nStep 2: ₦4,000 + ₦600 = ₦4,600.\nTherefore, the selling price is ₦4,600."),
            ("Find the simple interest on ₦12,000 at 8% per year for 2 years.", "Use I = PRT/100.", "1920", "Step 1: I = 12,000 × 8 × 2 ÷ 100.\nStep 2: I = 1,920.\nTherefore, the interest is ₦1,920."),
        ],
        "Challenge": [
            ("A trader marks an item at ₦10,000 and gives a 12% discount. Find the selling price.", "Subtract the discount from the marked price.", "8800", "Step 1: 12% of ₦10,000 = ₦1,200.\nStep 2: ₦10,000 - ₦1,200 = ₦8,800.\nTherefore, the selling price is ₦8,800."),
            ("An item is sold for ₦5,400 at a 10% loss. Find its cost price.", "The selling price represents 90% of the cost price.", "6000", "Step 1: 90% of the cost price is ₦5,400.\nStep 2: Cost price = 5,400 ÷ 0.9.\nTherefore, the cost price is ₦6,000."),
        ],
    },
    "Inequalities & Graphs": {
        "Easy": [
            ("Solve x + 3 < 9. What is the greatest whole-number value of x?", "Subtract 3 from both sides.", "5", "Step 1: x + 3 < 9.\nStep 2: Subtract 3: x < 6.\nThe greatest whole number less than 6 is 5."),
            ("For y = 2x + 1, find y when x = 3.", "Substitute 3 for x.", "7", "Step 1: y = 2(3) + 1.\nStep 2: y = 6 + 1.\nTherefore, y = 7."),
        ],
        "Medium": [
            ("Solve 3x ≤ 18. What is the greatest possible value of x?", "Divide both sides by 3.", "6", "Step 1: Divide both sides by positive 3.\nStep 2: x ≤ 6.\nTherefore, the greatest possible value is 6."),
            ("The point (4, y) lies on y = 3x - 2. Find y.", "Substitute x = 4.", "10", "Step 1: y = 3(4) - 2.\nStep 2: y = 12 - 2.\nTherefore, y = 10."),
        ],
        "Challenge": [
            ("Solve -2x > 10.", "Reverse the inequality sign when dividing by a negative number.", "x<-5", "Step 1: Divide both sides by -2.\nStep 2: Reverse > to <.\nTherefore, x < -5."),
            ("Find the gradient between (1, 3) and (5, 11).", "Use change in y divided by change in x.", "2", "Step 1: Change in y = 11 - 3 = 8.\nStep 2: Change in x = 5 - 1 = 4.\nGradient = 8 ÷ 4 = 2."),
        ],
    },
    "Geometry & Mensuration": {
        "Easy": [
            ("Find the perimeter of a rectangle 8 cm long and 5 cm wide.", "Use 2(length + width).", "26", "Step 1: Add length and width: 8 + 5 = 13.\nStep 2: Multiply by 2: 2 × 13 = 26.\nTherefore, the perimeter is 26 cm."),
            ("Find the area of a triangle with base 10 cm and height 6 cm.", "Use 1/2 × base × height.", "30", "Step 1: Area = 1/2 × 10 × 6.\nStep 2: Area = 30.\nTherefore, the area is 30 cm²."),
        ],
        "Medium": [
            ("Find the circumference of a circle with radius 7 cm. Use π = 22/7.", "Use C = 2πr.", "44", "Step 1: C = 2 × 22/7 × 7.\nStep 2: Cancel 7, giving 2 × 22.\nTherefore, the circumference is 44 cm."),
            ("A map uses a scale of 1 cm to 5 km. What distance does 7 cm represent?", "Multiply the map length by 5 km.", "35", "Step 1: Every 1 cm represents 5 km.\nStep 2: 7 × 5 = 35.\nTherefore, 7 cm represents 35 km."),
        ],
        "Challenge": [
            ("Find the volume of a cylinder with radius 7 cm and height 10 cm. Use π = 22/7.", "Use V = πr²h.", "1540", "Step 1: V = 22/7 × 7² × 10.\nStep 2: V = 22 × 7 × 10.\nTherefore, the volume is 1,540 cm³."),
            ("A right-angled triangle has shorter sides 6 cm and 8 cm. Find the hypotenuse.", "Use Pythagoras: c² = a² + b².", "10", "Step 1: c² = 6² + 8² = 36 + 64 = 100.\nStep 2: c = √100.\nTherefore, the hypotenuse is 10 cm."),
        ],
    },
    "Statistics & Probability": {
        "Easy": [
            ("Find the mean of 4, 6 and 8.", "Add the values and divide by how many there are.", "6", "Step 1: 4 + 6 + 8 = 18.\nStep 2: There are 3 values, so 18 ÷ 3 = 6.\nTherefore, the mean is 6."),
            ("A fair coin is tossed once. What is the probability of getting a head? Give a fraction.", "There is one favourable result out of two possible results.", "1/2", "Step 1: A coin has 2 equally likely outcomes.\nStep 2: One outcome is a head.\nTherefore, P(head) = 1/2."),
        ],
        "Medium": [
            ("Find the median of 3, 9, 5, 7 and 1.", "Arrange the numbers in order first.", "5", "Step 1: Order the values: 1, 3, 5, 7, 9.\nStep 2: The middle value is 5.\nTherefore, the median is 5."),
            ("A bag contains 3 red and 5 blue balls. What is the probability of choosing a red ball?", "Use favourable outcomes divided by total outcomes.", "3/8", "Step 1: Total balls = 3 + 5 = 8.\nStep 2: There are 3 red balls.\nTherefore, P(red) = 3/8."),
        ],
        "Challenge": [
            ("The mean of 6, 8, x and 10 is 9. Find x.", "Use total = mean × number of values.", "12", "Step 1: The required total is 9 × 4 = 36.\nStep 2: Known values total 6 + 8 + 10 = 24.\nStep 3: x = 36 - 24 = 12."),
            ("Two fair coins are tossed. What is the probability of getting two heads?", "List HH, HT, TH and TT.", "1/4", "Step 1: There are 4 equally likely outcomes: HH, HT, TH, TT.\nStep 2: Only HH gives two heads.\nTherefore, the probability is 1/4."),
        ],
    },
}

@dataclass
class PracticeState:
    topic: str
    difficulty: str
    class_level: str
    language: str
    question: str
    hint: str
    expected: str
    explanation: str
    target_count: int = 5
    correct: int = 0
    attempted: int = 0
    question_number: int = 1
    answered: bool = False
    last_correct: bool | None = None
    missed: list[dict] = field(default_factory=list)
    question_sets: dict[str, list[tuple[str, str, str, str]]] = field(default_factory=dict)
    session_id: str = field(default_factory=lambda: secrets.token_hex(12))


_sessions: dict[str, PracticeState] = {}
PRAISE_MESSAGES = (
    "Excellent work! You got it right.",
    "Well done! Your answer is correct.",
    "Great thinking! Keep it up.",
    "Brilliant! You solved that correctly.",
)


def _choose_question(topic: str, difficulty: str, previous: str = ""):
    return generate_question(topic, difficulty)


def _build_question_queue(topic: str, difficulty: str, count: int):
    """Build the full session up front so learners never see a repeated prompt."""
    questions = []
    seen = set()
    attempts = 0
    while len(questions) < count and attempts < count * 50:
        item = _choose_question(topic, difficulty)
        attempts += 1
        if item[0] not in seen:
            questions.append(item)
            seen.add(item[0])

    if len(questions) < count:
        raise RuntimeError("Unable to prepare a varied practice session")
    return questions


def start_practice(student_id: str, topic: str, difficulty: str, question_count: int = 5, class_level: str = "JSS2", language: str = "English") -> dict:
    # Keep old JSS2 API clients working while the classroom UI exposes only the
    # audited class-and-term curriculum.
    legacy_jss2_topic = class_level == "JSS2" and topic in QUESTION_BANK
    if class_level not in CLASS_TOPICS or (topic not in CLASS_TOPICS[class_level] and not legacy_jss2_topic) or difficulty not in {"Easy", "Medium", "Challenge"}:
        raise ValueError("Unsupported practice selection")
    if question_count not in {5, 10, 20}:
        raise ValueError("Unsupported question count")
    language = language if language in PRACTICE_TEXT else "English"
    source_questions = _build_question_queue(topic, difficulty, question_count)
    questions = translate_question_batch(source_questions, language)
    question, hint, expected, explanation = questions[0]
    state = PracticeState(
        topic, difficulty, class_level, language, question, hint, expected, explanation,
        target_count=question_count, question_sets={"English": source_questions, language: questions},
    )
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
    state.last_correct = correct
    if not correct:
        state.missed.append({
            "question_number": state.question_number,
            "learner_answer": answer.strip(),
        })
    completed = state.attempted >= state.target_count
    result = {
        **_answer_feedback(state, correct),
        "score": state.correct,
        "attempted": state.attempted,
        "percentage": round(state.correct / state.attempted * 100),
        "completed": completed,
    }
    if completed:
        result["summary"] = _summary(state)
    return result


def next_question(student_id: str) -> dict:
    state = _sessions.get(student_id)
    if not state:
        raise LookupError("No active practice session")
    if not state.answered:
        raise RuntimeError("Answer the current question first")
    if state.attempted >= state.target_count:
        raise RuntimeError("Practice session is complete")
    questions = state.question_sets[state.language]
    question, hint, expected, explanation = questions[state.question_number]
    state.question, state.hint, state.expected, state.explanation = question, hint, expected, explanation
    state.question_number += 1
    state.answered = False
    state.last_correct = None
    return _public_question(state)


def change_practice_language(student_id: str, language: str) -> dict:
    state = _sessions.get(student_id)
    if not state:
        raise LookupError("No active practice session")
    language = language if language in PRACTICE_TEXT else "English"
    if language not in state.question_sets:
        state.question_sets[language] = translate_question_batch(state.question_sets["English"], language)
    state.language = language
    question, hint, expected, explanation = state.question_sets[language][state.question_number - 1]
    state.question, state.hint, state.expected, state.explanation = question, hint, expected, explanation
    result = _public_question(state)
    result["answered"] = state.answered
    if state.answered:
        result["feedback"] = _answer_feedback(state, bool(state.last_correct))
        if state.attempted >= state.target_count:
            result["summary"] = _summary(state)
    return result


def _answer_feedback(state: PracticeState, correct: bool) -> dict:
    return {
        "correct": correct,
        "message": secrets.choice(PRACTICE_TEXT[state.language]["correct"]) if correct else PRACTICE_TEXT[state.language]["attempt"],
        "expected_answer": state.expected,
        "correct_answer_label": PRACTICE_TEXT[state.language]["correct_answer"],
        "explanation": state.explanation,
    }


def _public_question(state: PracticeState) -> dict:
    return {
        "session_id": state.session_id,
        "class_level": state.class_level,
        "topic": state.topic,
        "difficulty": state.difficulty,
        "language": state.language,
        "question": state.question,
        "hint": state.hint,
        "question_number": state.question_number,
        "score": state.correct,
        "attempted": state.attempted,
        "total_questions": state.target_count,
    }


def _summary(state: PracticeState) -> dict:
    percentage = round(state.correct / state.attempted * 100) if state.attempted else 0
    if state.language != "English":
        language_instruction = {
            "Yoruba": "Ṣe àtúnyẹ̀wò àwọn ìbéèrè tí o kò rí, kí o sì tún ṣe ìdánwò náà.",
            "Igbo": "Legharịa ajụjụ ndị ị na-azaghị nke ọma ma megharịa omume a.",
            "Hausa": "Sake duba tambayoyin da ba ka amsa daidai ba, sannan ka sake gwadawa.",
        }[state.language]
        if percentage >= 80:
            recommendation = {
                "Yoruba": f"O ṣe dáadáa ní {state.topic}. Gbìyànjú ipele tó kàn.",
                "Igbo": f"Ị mere nke ọma na {state.topic}. Gbalịa ọkwa na-esote.",
                "Hausa": f"Ka yi kyau a {state.topic}. Gwada mataki na gaba.",
            }[state.language]
        else:
            recommendation = language_instruction
    elif percentage >= 80:
        recommendation = f"Strong work in {state.topic}. Try the next difficulty level when you are ready."
    elif percentage >= 50:
        recommendation = f"You are making progress in {state.topic}. Review the missed questions and practise once more."
    else:
        recommendation = f"Review the worked examples for {state.topic}, then try an easier session before moving up."
    return {
        "session_id": state.session_id,
        "class_level": state.class_level,
        "topic": state.topic,
        "difficulty": state.difficulty,
        "score": state.correct,
        "attempted": state.attempted,
        "percentage": percentage,
        "missed": [
            {
                "question": state.question_sets[state.language][item["question_number"] - 1][0],
                "learner_answer": item["learner_answer"],
                "correct_answer": state.question_sets[state.language][item["question_number"] - 1][2],
                "explanation": state.question_sets[state.language][item["question_number"] - 1][3],
            }
            for item in state.missed
        ],
        "recommendation": recommendation,
    }
