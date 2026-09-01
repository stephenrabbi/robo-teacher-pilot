"""Offline safety/sanity tests for V2.3 voice tutoring."""
from tutor import SUPPORTED_AUDIO_MIME_TYPES, MAX_AUDIO_BYTES, get_tutor_audio_reply
from telegram_adapter import MAX_AUDIO_BYTES as ADAPTER_MAX_AUDIO_BYTES

assert "audio/ogg" in SUPPORTED_AUDIO_MIME_TYPES
assert "audio/opus" in SUPPORTED_AUDIO_MIME_TYPES
assert MAX_AUDIO_BYTES == ADAPTER_MAX_AUDIO_BYTES

try:
    get_tutor_audio_reply("TEST001", b"abc", "audio/unsupported")
    raise AssertionError("Unsupported audio MIME should be rejected")
except ValueError:
    pass

try:
    get_tutor_audio_reply("TEST001", b"", "audio/ogg")
    raise AssertionError("Empty audio should be rejected")
except ValueError:
    pass

try:
    get_tutor_audio_reply("TEST001", b"x" * (MAX_AUDIO_BYTES + 1), "audio/ogg")
    raise AssertionError("Oversized audio should be rejected")
except ValueError:
    pass

print("V2.3 voice safety tests passed")
