import unittest
from trusted_assessment_scoring import score_assessment


class TestTrustedScoring(unittest.TestCase):
    def setUp(self):
        self.key = {"q1": "B", "q2": "C", "q3": "A", "q4": "D"}

    def test_server_computes_score_from_answers(self):
        self.assertEqual(score_assessment(answers={"q1": "B", "q2": "X", "q3": "A", "q4": "D"}, answer_key=self.key),
                         {"correct": 3, "total": 4, "percentage": 75})

    def test_reject_missing_or_extra_question(self):
        for answers in ({"q1": "B"}, {**self.key, "q5": "A"}):
            with self.assertRaises(ValueError):
                score_assessment(answers=answers, answer_key=self.key)

    def test_reject_empty_key(self):
        with self.assertRaises(ValueError):
            score_assessment(answers={}, answer_key={})

    def test_reject_bad_choices(self):
        with self.assertRaises(ValueError):
            score_assessment(answers={**self.key, "q3": None}, answer_key=self.key)

    def test_does_not_accept_client_claimed_score(self):
        with self.assertRaises(TypeError):
            score_assessment(answers=self.key, answer_key=self.key, mastery_score=100)


if __name__ == "__main__":
    unittest.main()
