import unittest
from unittest.mock import patch

from maths_mouth_cues import _validated_header, prepare_cued_audio


class TestMathsMouthCues(unittest.TestCase):
    def test_disabled_does_not_read_pcm_ahead(self):
        source = iter((b"ab", b"cd"))
        audio, header = prepare_cued_audio(source, None)
        self.assertIs(audio, source)
        self.assertIsNone(header)

    def test_large_stream_preserves_every_byte_without_analysis(self):
        chunks = (bytes(384_000), b"ab", b"cd")
        with patch("maths_mouth_cues._mouth_cue_header") as analyse:
            audio, header = prepare_cued_audio(iter(chunks), "rhubarb")
        analyse.assert_not_called()
        self.assertEqual(b"".join(audio), b"".join(chunks))
        self.assertIsNone(header)

    def test_unavailable_analyser_returns_original_pcm(self):
        audio, header = prepare_cued_audio(iter((b"ab", b"cd")), "/missing/rhubarb")
        self.assertEqual(b"".join(audio), b"abcd")
        self.assertIsNone(header)

    def test_rejects_unknown_and_overlapping_cues(self):
        first = {"start": 0, "end": .5, "value": "X"}
        self.assertIsNotNone(_validated_header({"mouthCues": [first]}, 1))
        for cue in (
            {"start": .4, "end": .8, "value": "F"},
            {"start": .5, "end": .8, "value": "unknown"},
            {"start": .5, "end": 1.2, "value": "F"},
        ):
            self.assertIsNone(_validated_header({"mouthCues": [first, cue]}, 1))
