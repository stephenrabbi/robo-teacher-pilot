"""Check JSS1 vowel instruction scope without calling an AI provider."""
import ast
from pathlib import Path
import unittest


def instruction_function():
    tree = ast.parse(Path(__file__).with_name("subject_tutor.py").read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "subject_instruction")
    namespace = {"SUBJECTS": ("English Language", "Basic Science")}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "subject_tutor.py", "exec"), namespace)
    return namespace["subject_instruction"]


class EnglishVowelGuidanceTests(unittest.TestCase):
    def test_jss1_preserves_examples_and_pronunciation_limits_in_all_languages(self):
        instruction = instruction_function()
        for language in ("English", "Yoruba", "Igbo", "Hausa"):
            with self.subTest(language=language):
                text = instruction("English Language", language, "JSS1")
                for fragment in ("/iː/ and /ɪ/", "sleep/slip", "short English sentences",
                                 "Wait for their answer", "word choice only", "never proof of correct",
                                 "Do not claim to have heard", "inventing a pronunciation score"):
                    self.assertIn(fragment, text)
                self.assertIn("Preserve English example sentences", text)

    def test_jss1_activity_does_not_leak_to_other_classes_or_subjects(self):
        instruction = instruction_function()
        for subject, level in (("English Language", "JSS2"), ("English Language", "JSS3"), ("Basic Science", "JSS1")):
            with self.subTest(subject=subject, level=level):
                self.assertNotIn("sleep/slip", instruction(subject, "English", level))


if __name__ == "__main__":
    unittest.main()
