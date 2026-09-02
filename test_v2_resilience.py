"""Controlled failure-path tests for Robo-Teacher V2.

These tests deliberately mock provider/media failures. They never touch live
Telegram, Gemini, Google Sheets, or learner data.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import main
import tutor


async def test_telegram_text_fallback():
    sent = AsyncMock()
    with patch.object(main, "get_tutor_reply", side_effect=RuntimeError("simulated provider failure")), \
         patch.object(main, "send_telegram_message", sent), \
         patch.object(main, "log_interaction") as logged:
        await main._handle_telegram_message(123, "Explain fractions", "TEST001", "V2 Staging Test", "TEST001-2026-09-02")
        reply = sent.await_args.args[1]
        assert "technical hiccup" in reply.lower()
        assert logged.call_args.args[-1] == "Error"


async def test_telegram_image_fallback():
    sent = AsyncMock()
    with patch.object(main, "download_telegram_image", side_effect=RuntimeError("simulated download failure")), \
         patch.object(main, "send_telegram_message", sent), \
         patch.object(main, "log_interaction") as logged:
        await main._handle_telegram_image(123, "file-id", "", "TEST001", "V2 Staging Test", "TEST001-2026-09-02")
        reply = sent.await_args.args[1]
        assert "couldn't read that image" in reply.lower()
        assert logged.call_args.args[-1] == "Error"


async def test_telegram_audio_fallback():
    sent = AsyncMock()
    with patch.object(main, "download_telegram_audio", side_effect=RuntimeError("simulated download failure")), \
         patch.object(main, "send_telegram_message", sent), \
         patch.object(main, "log_interaction") as logged:
        await main._handle_telegram_audio(123, "file-id", "audio/ogg", "TEST001", "V2 Staging Test", "TEST001-2026-09-02")
        reply = sent.await_args.args[1]
        assert "couldn't understand that voice note" in reply.lower()
        assert logged.call_args.args[-1] == "Error"


def _patched_tutor_context():
    return (
        patch.object(tutor, "_safe_profile_update", return_value=dict(tutor.DEFAULT_PROFILE)),
        patch.object(tutor, "_get_client", return_value=object()),
    )


def test_rate_limit_fallback():
    profile_patch, client_patch = _patched_tutor_context()
    with profile_patch, client_patch, \
         patch.object(tutor, "_ask", side_effect=RuntimeError("429 RESOURCE_EXHAUSTED quota")):
        reply, latency = tutor.get_tutor_reply("TEST001", "Please explain ratio")
        assert "try again in about a minute" in reply.lower()
        assert latency >= 0


def test_retry_failure_returns_safe_fallback():
    profile_patch, client_patch = _patched_tutor_context()
    with profile_patch, client_patch, \
         patch.object(tutor, "_ask", side_effect=[RuntimeError("temporary provider failure"), RuntimeError("provider still unavailable")]) as ask:
        reply, latency = tutor.get_tutor_reply("TEST001", "Please explain ratio")
        assert "technical hiccup" in reply.lower()
        assert ask.call_count == 2
        assert latency >= 0


def test_retry_rate_limit_returns_rate_limit_fallback():
    profile_patch, client_patch = _patched_tutor_context()
    with profile_patch, client_patch, \
         patch.object(tutor, "_ask", side_effect=[RuntimeError("temporary provider failure"), RuntimeError("429 RESOURCE_EXHAUSTED quota")]) as ask:
        reply, latency = tutor.get_tutor_reply("TEST001", "Please explain ratio")
        assert "try again in about a minute" in reply.lower()
        assert ask.call_count == 2
        assert latency >= 0


def test_client_initialization_failure_returns_safe_fallback():
    with patch.object(tutor, "_safe_profile_update", return_value=dict(tutor.DEFAULT_PROFILE)), \
         patch.object(tutor, "_get_client", side_effect=KeyError("GEMINI_API_KEY")):
        reply, latency = tutor.get_tutor_reply("TEST001", "Please explain ratio")
        assert "technical hiccup" in reply.lower()
        assert latency >= 0


asyncio.run(test_telegram_text_fallback())
asyncio.run(test_telegram_image_fallback())
asyncio.run(test_telegram_audio_fallback())
test_rate_limit_fallback()
test_retry_failure_returns_safe_fallback()
test_retry_rate_limit_returns_rate_limit_fallback()
test_client_initialization_failure_returns_safe_fallback()
print("V2 controlled resilience/fallback tests passed.")
