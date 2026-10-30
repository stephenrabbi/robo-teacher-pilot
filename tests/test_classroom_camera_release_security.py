"""Synthetic camera-upload release checks; no real images or Gemini requests."""
import asyncio
import io
import unittest
from unittest.mock import patch
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers
from classroom_api import ClassroomSessionRequest, create_classroom_session, classroom_image

def upload(mime,data=b"synthetic"):
    return UploadFile(file=io.BytesIO(data),filename="test.bin",headers=Headers({"content-type":mime}))

class CameraReleaseTest(unittest.TestCase):
    def setUp(self):
        self.a=create_classroom_session(ClassroomSessionRequest(nickname="CameraA",class_level="JSS2"))
        self.b=create_classroom_session(ClassroomSessionRequest(nickname="CameraB",class_level="JSS2"))

    def invoke(self, token, mime, data=b"synthetic"):
        return asyncio.run(classroom_image(
            session_token=token,image=upload(mime,data),
            caption="Synthetic Maths image",language="English"))

    def test_forged_learner_identity_rejected(self):
        p=self.a["session_token"].split(".");p[0]=self.b["learner_id"]
        with patch("classroom_api.get_tutor_image_reply") as provider:
            with self.assertRaises(HTTPException) as e:
                self.invoke(".".join(p),"image/png")
        self.assertEqual(e.exception.status_code,401)
        provider.assert_not_called()

    def test_unsupported_media_rejected(self):
        with patch("classroom_api.get_tutor_image_reply") as provider:
            with self.assertRaises(HTTPException) as e:
                self.invoke(self.a["session_token"],"application/pdf")
        self.assertEqual(e.exception.status_code,415)
        provider.assert_not_called()

    def test_empty_image_rejected(self):
        with patch("classroom_api.get_tutor_image_reply") as provider:
            with self.assertRaises(HTTPException) as e:
                self.invoke(self.a["session_token"],"image/png",b"")
        self.assertEqual(e.exception.status_code,422)
        provider.assert_not_called()

if __name__=="__main__":
    unittest.main()
