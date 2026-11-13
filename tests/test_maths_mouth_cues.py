import gzip
import json
import unittest

from maths_mouth_cues import _NARRATION_DIR, _validated_header, prepared_maths_narration


class TestMathsMouthCues(unittest.TestCase):
    def test_prepared_cues_match_original_pcm(self):
        pcm, header = prepared_maths_narration(
            "Add two to both sides of the equation.", "English", "female", "normal"
        )
        self.assertEqual(pcm, gzip.decompress((_NARRATION_DIR / "add-two-both-sides.pcm.gz").read_bytes()))
        self.assertGreater(len(json.loads(header)), 1)
        self.assertLessEqual(json.loads(header)[-1]["end"], len(pcm) / 48_000)

    def test_settings_and_text_must_match_the_recording(self):
        text = "Add two to both sides of the equation."
        for request in (
            ("Add three to both sides.", "English", "female", "normal"),
            (text, "Yoruba", "female", "normal"),
            (text, "English", "male", "normal"),
            (text, "English", "female", "slower"),
        ):
            self.assertIsNone(prepared_maths_narration(*request))

    def test_rejects_unknown_and_overlapping_cues(self):
        first = {"start": 0, "end": .5, "value": "X"}
        self.assertIsNotNone(_validated_header({"mouthCues": [first]}, 1))
        for cue in (
            {"start": .4, "end": .8, "value": "F"},
            {"start": .5, "end": .8, "value": "unknown"},
            {"start": .5, "end": 1.2, "value": "F"},
        ):
            self.assertIsNone(_validated_header({"mouthCues": [first, cue]}, 1))


class TestMathsNarrationSpeechRoute(unittest.IsolatedAsyncioTestCase):
    async def test_prepared_audio_and_uncued_fallback(self):
        from unittest.mock import patch

        from classroom_api import ClassroomSpeech, classroom_speech

        text = "Add two to both sides of the equation."
        audio, cues = prepared_maths_narration(text, "English", "female", "normal")
        with (
            patch("classroom_api._verify_session", return_value="maths-audio-test"),
            patch("classroom_api._enforce_rate_limit"),
            patch("classroom_api.stream_tutor_speech", return_value=iter([b"\0\0"])) as provider,
        ):
            settings = dict(text=text, session_token="synthetic-maths-speech-token", language="English",
                            voice_gender="female", pace="normal")
            prepared = classroom_speech(ClassroomSpeech(**settings, mouth_cues=True))
            self.assertEqual(prepared.headers["X-Robo-Mouth-Cues"], cues)
            self.assertEqual(b"".join([chunk async for chunk in prepared.body_iterator]), audio)
            provider.assert_not_called()

            fallback = classroom_speech(ClassroomSpeech(**settings))
            self.assertNotIn("X-Robo-Mouth-Cues", fallback.headers)
            self.assertEqual(b"".join([chunk async for chunk in fallback.body_iterator]), b"\0\0")
            provider.assert_called_once_with(text, "English", "female", "normal")
