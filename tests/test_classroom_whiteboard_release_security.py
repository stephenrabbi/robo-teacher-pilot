"""Synthetic authorization and input-validation checks for classroom whiteboards."""
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from classroom_api import (
    ClassroomSessionRequest, ClassroomWhiteboard,
    create_classroom_session, classroom_whiteboard,
)

PNG="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"

class WhiteboardReleaseSecurityTest(unittest.TestCase):
    def setUp(self):
        self.a=create_classroom_session(ClassroomSessionRequest(nickname="WB-A",class_level="JSS2"))
        self.b=create_classroom_session(ClassroomSessionRequest(nickname="WB-B",class_level="JSS2"))

    def test_forged_identity_is_rejected_before_provider_call(self):
        pieces=self.a["session_token"].split(".")
        pieces[0]=self.b["learner_id"]
        forged=".".join(pieces)
        with patch("classroom_api.get_tutor_image_reply") as provider:
            with self.assertRaises(HTTPException) as caught:
                classroom_whiteboard(ClassroomWhiteboard(session_token=forged,image_data=PNG))
        self.assertEqual(caught.exception.status_code,401)
        provider.assert_not_called()

    def test_invalid_base64_is_rejected_before_provider_call(self):
        with patch("classroom_api.get_tutor_image_reply") as provider:
            with self.assertRaises(HTTPException) as caught:
                classroom_whiteboard(ClassroomWhiteboard(
                    session_token=self.a["session_token"],
                    image_data="data:image/png;base64,INVALID-BASE64-PAYLOAD"))
        self.assertEqual(caught.exception.status_code,422)
        provider.assert_not_called()

    def test_unexpected_media_format_is_rejected(self):
        with patch("classroom_api.get_tutor_image_reply") as provider:
            with self.assertRaises(HTTPException) as caught:
                classroom_whiteboard(ClassroomWhiteboard(
                    session_token=self.a["session_token"],
                    image_data="data:image/jpeg;base64,AAAABBBBCCCCDDDD"))
        self.assertEqual(caught.exception.status_code,415)
        provider.assert_not_called()

if __name__=="__main__":
    unittest.main()
