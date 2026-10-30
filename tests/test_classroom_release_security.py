"""Release-gate checks for classroom session ownership and teacher access.

Uses synthetic sessions and mocks; no provider, database, or real learner records.
"""
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from classroom_api import (
    ClassroomSessionRequest, PracticeProgress, TeacherDashboardRequest,
    create_classroom_session, classroom_practice_progress,
    classroom_teacher_dashboard,
)

class ClassroomReleaseSecurityTest(unittest.TestCase):
    def test_session_isolation_for_progress(self):
        a=create_classroom_session(ClassroomSessionRequest(nickname="QA-A",class_level="JSS2"))
        b=create_classroom_session(ClassroomSessionRequest(nickname="QA-B",class_level="JSS2"))
        self.assertNotEqual(a["learner_id"],b["learner_id"])
        with patch("classroom_api.build_dashboard",side_effect=lambda learner,level: {"owner":learner}) as dashboard:
            ra=classroom_practice_progress(PracticeProgress(session_token=a["session_token"],class_level="JSS2"))
            rb=classroom_practice_progress(PracticeProgress(session_token=b["session_token"],class_level="JSS2"))
        self.assertEqual(ra["owner"],a["learner_id"])
        self.assertEqual(rb["owner"],b["learner_id"])
        self.assertEqual(dashboard.call_count,2)

    def test_forged_session_cannot_retrieve_progress(self):
        a=create_classroom_session(ClassroomSessionRequest(nickname="QA-A",class_level="JSS2"))
        b=create_classroom_session(ClassroomSessionRequest(nickname="QA-B",class_level="JSS2"))
        pieces=a["session_token"].split(".")
        pieces[0]=b["learner_id"]
        forged=".".join(pieces)
        with patch("classroom_api.build_dashboard") as dashboard:
            with self.assertRaises(HTTPException) as caught:
                classroom_practice_progress(PracticeProgress(session_token=forged,class_level="JSS2"))
        self.assertEqual(caught.exception.status_code,401)
        dashboard.assert_not_called()

    def test_teacher_dashboard_not_accessible_without_private_key(self):
        with patch.dict("os.environ",{"TEACHER_DASHBOARD_KEY":"qa-secret-key-123456"},clear=False):
            with patch("classroom_api.build_teacher_dashboard") as dashboard:
                with self.assertRaises(HTTPException) as caught:
                    classroom_teacher_dashboard(TeacherDashboardRequest(access_key="wrong-secret-key-123",class_level="JSS2"))
            self.assertEqual(caught.exception.status_code,403)
            dashboard.assert_not_called()

if __name__=="__main__":
    unittest.main()
