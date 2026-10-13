"""Guard the existing server-graded practice API contract.

No production Supabase calls. Structural regression assertions intentionally
target the current practice endpoint, not a new grading implementation.
"""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestPracticeServerScoreBoundary(unittest.TestCase):
    def test_answer_schema_does_not_accept_client_score_or_correctness(self):
        tree = ast.parse((ROOT / "classroom_api.py").read_text(encoding="utf-8"))
        request = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "PracticeAnswer")
        fields = {node.target.id for node in request.body if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)}
        self.assertEqual(fields, {"session_token", "answer"})

    def test_answer_handler_calls_server_grader(self):
        source = (ROOT / "classroom_api.py").read_text(encoding="utf-8")
        self.assertIn("result = answer_practice(student_id, submission.answer)", source)
        self.assertIn('if result["completed"]:', source)
        self.assertIn("background_tasks.add_task(save_result, student_id, result[\"summary\"])", source)

    def test_correctness_is_computed_from_server_expected_answer(self):
        source = (ROOT / "practice.py").read_text(encoding="utf-8")
        self.assertIn("correct = _normalise_answer(answer) == _normalise_answer(state.expected)", source)


if __name__ == "__main__":
    unittest.main()
