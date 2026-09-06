"""Short class-and-term diagnostic assessments kept separate from Practice history."""

import secrets
from dataclasses import dataclass, field

from curriculum import CURRICULUM
from practice import _normalise_answer
from practice_generator import generate_question
from practice_translation import PRACTICE_TEXT, translate_question_batch


@dataclass
class DiagnosticState:
    class_level: str
    term: str
    language: str
    questions: list[dict]
    index: int = 0
    correct: int = 0
    answered: bool = False
    results: list[dict] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: secrets.token_hex(12))


_sessions: dict[str, DiagnosticState] = {}


def _build_questions(class_level: str, term: str, count: int = 10) -> list[dict]:
    topics = CURRICULUM[class_level][term]
    questions, seen, attempt = [], set(), 0
    while len(questions) < count and attempt < count * 60:
        topic = topics[len(questions) % len(topics)]
        difficulty = "Easy" if len(questions) < len(topics) else "Medium"
        item = generate_question(topic, difficulty);attempt += 1
        if item[0] in seen: continue
        seen.add(item[0]);questions.append({"topic": topic, "difficulty": difficulty, "source_item": item, "item": item})
    if len(questions) < count: raise RuntimeError("Unable to prepare diagnostic assessment")
    return questions


def start_diagnostic(student_id: str, class_level: str, term: str, language: str) -> dict:
    if class_level not in CURRICULUM or term not in CURRICULUM[class_level]: raise ValueError("Unsupported diagnostic selection")
    language = language if language in PRACTICE_TEXT else "English"
    questions = _build_questions(class_level, term)
    translated = translate_question_batch([q["item"] for q in questions], language)
    for question, item in zip(questions, translated): question["item"] = item
    state = DiagnosticState(class_level, term, language, questions);_sessions[student_id] = state
    return _public(state)


def answer_diagnostic(student_id: str, answer: str) -> dict:
    state = _sessions.get(student_id)
    if not state: raise LookupError("No active diagnostic")
    if state.answered: raise RuntimeError("Question already answered")
    current = state.questions[state.index];question, _hint, expected, explanation = current["item"]
    correct = _normalise_answer(answer) == _normalise_answer(expected)
    state.correct += int(correct);state.answered = True
    state.results.append({"topic": current["topic"], "correct": correct, "question": question, "learner_answer": answer.strip(), "correct_answer": expected, "explanation": explanation})
    completed = state.index + 1 >= len(state.questions)
    messages = PRACTICE_TEXT[state.language]
    attempted = state.index + 1
    result = {"correct": correct, "message": secrets.choice(messages["correct"]) if correct else messages["attempt"], "correct_answer_label": messages["correct_answer"], "expected_answer": expected, "explanation": explanation, "score": state.correct, "attempted": attempted, "percentage": round(state.correct / attempted * 100), "completed": completed}
    if completed: result["summary"] = _summary(state)
    return result


def next_diagnostic(student_id: str) -> dict:
    state = _sessions.get(student_id)
    if not state: raise LookupError("No active diagnostic")
    if not state.answered: raise RuntimeError("Answer current question")
    if state.index + 1 >= len(state.questions): raise RuntimeError("Diagnostic complete")
    state.index += 1;state.answered = False
    return _public(state)


def change_diagnostic_language(student_id: str, language: str) -> dict:
    state = _sessions.get(student_id)
    if not state: raise LookupError("No active diagnostic")
    language = language if language in PRACTICE_TEXT else "English"
    translated = translate_question_batch([q["source_item"] for q in state.questions], language)
    for question, item in zip(state.questions, translated): question["item"] = item
    state.language = language;result = _public(state);result["answered"] = state.answered
    if state.answered:
        last = state.results[-1];messages = PRACTICE_TEXT[language];current = state.questions[state.index]["item"]
        result["feedback"] = {"correct": last["correct"], "message": secrets.choice(messages["correct"]) if last["correct"] else messages["attempt"], "correct_answer_label": messages["correct_answer"], "expected_answer": current[2], "explanation": current[3]}
    return result


def _public(state: DiagnosticState) -> dict:
    current = state.questions[state.index];question, hint, _expected, _explanation = current["item"]
    return {"session_id": state.session_id, "class_level": state.class_level, "topic": f"{state.term} Diagnostic", "difficulty": current["difficulty"], "question": question, "hint": hint, "question_number": state.index + 1, "score": state.correct, "attempted": state.index, "total_questions": len(state.questions)}


def _summary(state: DiagnosticState) -> dict:
    topic_rows=[]
    for topic in CURRICULUM[state.class_level][state.term]:
        items=[r for r in state.results if r["topic"]==topic]
        if items: topic_rows.append({"topic":topic,"correct":sum(r["correct"] for r in items),"attempted":len(items),"percentage":round(sum(r["correct"] for r in items)/len(items)*100)})
    focus=min(topic_rows,key=lambda row:(row["percentage"],row["topic"]));percentage=round(state.correct/len(state.results)*100)
    level="Easy" if percentage<50 else "Medium" if percentage<80 else "Challenge"
    return {"session_id":state.session_id,"class_level":state.class_level,"term":state.term,"topic":f"{state.term} Diagnostic","difficulty":"Diagnostic","score":state.correct,"attempted":len(state.results),"percentage":percentage,"missed":[r for r in state.results if not r["correct"]],"topic_results":topic_rows,"recommended_topic":focus["topic"],"recommended_difficulty":level,"recommendation":f"Begin with {focus['topic']} at {level} level. Review each worked explanation before regular Practice.","diagnostic":True}
