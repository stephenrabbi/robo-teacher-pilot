"""Non-destructive release gate for preserved Classroom 2.0 feature wiring.

This asserts availability of UI controls and backend routes, not successful
end-to-end operation on physical devices or with live learner records.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"classroom/index.html").read_text(encoding="utf-8")
APP=(ROOT/"classroom/app.js").read_text(encoding="utf-8")
API=(ROOT/"classroom_api.py").read_text(encoding="utf-8")

class FeaturePreservationTest(unittest.TestCase):
    def test_classroom_tools_and_teacher_dashboard_have_controls(self):
        for item in (
            "teacherDashboard","openTeacherDashboard","whiteboard",
            "whiteboardButton","imageUpload","cameraCapture","cameraButton",
            "practiceArea","startPractice","startDiagnostic","language",
            "languageButton","readAnswer","canvasAnswer",
        ):
            with self.subTest(control=item):
                self.assertIn('id="'+item+'"',HTML)

    def test_backend_classroom_routes_are_preserved(self):
        for route in (
            '/teacher/dashboard','/practice/start','/practice/answer',
            '/practice/progress','/diagnostic/start','/diagnostic/answer',
            '/image','/whiteboard','/translate','/speech','/chat',
        ):
            with self.subTest(route=route):
                self.assertIn('@router.post("'+route+'"',API)

    def test_legal_pages_are_linked(self):
        for page in (
            "privacy.html","terms-of-use.html","terms-and-conditions.html",
            "cookie-policy.html","refund-policy.html",
        ):
            with self.subTest(page=page):
                self.assertIn('/classroom/'+page,HTML)
                self.assertTrue((ROOT/"classroom"/page).is_file())

    def test_learner_screen_switch_is_preserved(self):
        self.assertIn("function enterClassroomView()",APP)
        self.assertIn("function leaveClassroomView()",APP)
        self.assertIn("question.focus({preventScroll:true})",APP)

if __name__=="__main__":
    unittest.main()
