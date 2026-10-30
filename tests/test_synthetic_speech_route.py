"""Synthetic speech route checks. No paid model requests or real learner data."""
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from classroom_api import (
    ClassroomSessionRequest, ClassroomSpeech,
    create_classroom_session, classroom_speech
)


class ClassroomSpeechRouteTests(unittest.TestCase):
    def setUp(self):
        session = create_classroom_session(
            ClassroomSessionRequest(nickname="SyntheticVoiceQA", class_level="JSS2")
        )
        self.payload = ClassroomSpeech(
            session_token=session["session_token"], language="English",
            text="Three quarters plus one eighth equals seven eighths.",
            voice_gender="female", pace="normal"
        )

    def test_primary_audio_first_chunk_and_headers(self):
        with patch("classroom_api.stream_tutor_speech", return_value=iter((b"audio1", b"audio2"))) as primary:
            response = classroom_speech(self.payload)
        self.assertEqual(response.media_type, "audio/l16;rate=24000;channels=1")
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["x-audio-sample-rate"], "24000")
        self.assertIsNotNone(response.body_iterator)
        primary.assert_called_once_with(
            self.payload.text, "English", "female", "normal"
        )

    def test_empty_primary_stream_uses_stable_voice_fallback(self):
        with patch("classroom_api.stream_tutor_speech", return_value=iter(())), \
             patch("classroom_api.stream_stable_tutor_speech", return_value=iter((b"fallback",))) as fallback:
            response = classroom_speech(self.payload)
        self.assertIsNotNone(response.body_iterator)
        fallback.assert_called_once()

    def test_both_voice_services_unavailable_returns_safe_error(self):
        with patch("classroom_api.stream_tutor_speech", side_effect=RuntimeError("private-primary")), \
             patch("classroom_api.stream_stable_tutor_speech", side_effect=RuntimeError("private-fallback")):
            with self.assertRaises(HTTPException) as raised:
                classroom_speech(self.payload)
        self.assertEqual(raised.exception.status_code, 503)
        self.assertNotIn("private", raised.exception.detail)


if __name__ == "__main__":
    unittest.main()
