"""Prototype deterministic scoring boundary. Not connected to live classroom.

The answer key is supplied by trusted server code, NEVER from a client request.
This evaluates only fixed-choice assessments; free-form tutoring needs separate review.
"""
from collections.abc import Mapping, Sequence


def score_assessment(*, answers: Mapping[str, str], answer_key: Mapping[str, str]) -> dict:
    """Score a complete fixed-choice submission using an internal answer key.

    Caller/server MUST establish authenticated ownership, verified assessment
    assignment, attempt authorization, server-side question set, and rate limits
    before calling. No user_id, school code, correct flags or mastery score are
    accepted here.
    """
    if not answer_key:
        raise ValueError("Answer key cannot be empty")
    if not isinstance(answers, Mapping) or not isinstance(answer_key, Mapping):
        raise ValueError("Answers and key must be mappings")
    if set(answers) != set(answer_key):
        raise ValueError("Answer exactly the assigned questions")
    for question_id, correct_choice in answer_key.items():
        submitted = answers[question_id]
        if not isinstance(question_id, str) or not question_id:
            raise ValueError("Invalid question ID")
        if not isinstance(submitted, str) or not isinstance(correct_choice, str):
            raise ValueError("Choices must be strings")
        if not submitted or not correct_choice or len(submitted) > 64 or len(correct_choice) > 64:
            raise ValueError("Invalid choice")
    correct_count = sum(answers[q] == expected for q, expected in answer_key.items())
    total = len(answer_key)
    return {"correct": correct_count, "total": total,
            "percentage": (correct_count * 100) // total}
