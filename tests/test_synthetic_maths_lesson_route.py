"""Synthetic classroom Maths chat tests: no provider calls or student data."""
import unittest
from unittest.mock import patch
from starlette.requests import Request
from fastapi import HTTPException

from classroom_api import (
    ClassroomQuestion,
    ClassroomSessionRequest,
    classroom_chat,
    create_classroom_session,
)


class MathsLessonRouteTest(unittest.TestCase):
    def setUp(self):
        self.session = create_classroom_session(
            ClassroomSessionRequest(nickname="SyntheticMathsQA", class_level="JSS2")
        )
        self.request = Request({"type": "http", "method": "POST",
                                "path": "/api/classroom/chat", "headers": []})

    def test_fraction_question_passes_context_and_returns_steps(self):
        message = "What is 3/4 + 1/8? Explain each step."
        expected = "Step 1: 3/4 = 6/8. Step 2: 6/8 + 1/8 = 7/8."
        with patch("classroom_api.get_tutor_reply", return_value=(expected, 0.25)) as tutor:
            result = classroom_chat(ClassroomQuestion(
                session_token=self.session["session_token"],
                message=message, language="English"
            ), self.request)
        tutor.assert_called_once_with(
            self.session["learner_id"], message, "English", "JSS2"
        )
        self.assertEqual(result["reply"], expected)
        self.assertEqual(result["latency_seconds"], 0.25)
        self.assertEqual(result["learner_id"], self.session["learner_id"])

    def test_provider_errors_are_sanitized(self):
        with patch("classroom_api.get_tutor_reply", side_effect=RuntimeError("mock secret")):
            with self.assertRaises(HTTPException) as caught:
                classroom_chat(ClassroomQuestion(
                    session_token=self.session["session_token"],
                    message="Explain fractions", language="English"
                ), self.request)
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("secret", str(caught.exception.detail))


if __name__ == "__main__":
    unittest.main()
