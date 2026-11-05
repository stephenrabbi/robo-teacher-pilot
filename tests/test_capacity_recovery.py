"""Provider failure recovery without live calls or learner data."""
from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import classroom_api
import tutor


def test_capacity_retry_recovers_with_same_context():
    history = ["synthetic previous turn"]
    with patch.object(tutor, "_ask", side_effect=[RuntimeError("429 RESOURCE_EXHAUSTED"), ("A lesson", ["new turn"])]) as ask, patch.object(tutor.time, "sleep") as sleep:
        result = tutor._ask_with_capacity_retry(object(), history, "synthetic question", {}, "English", "JSS2")
    assert result == ("A lesson", ["new turn"])
    assert ask.call_args_list[0].args == ask.call_args_list[1].args
    assert ask.call_args.args[1] is history
    sleep.assert_called_once_with(1)


def test_capacity_retries_are_bounded_and_logs_do_not_contain_payload(caplog):
    with patch.object(tutor, "_ask", side_effect=RuntimeError("429 quota private-provider-payload")) as ask, patch.object(tutor.time, "sleep") as sleep:
        with pytest.raises(RuntimeError):
            tutor._ask_with_capacity_retry(object(), [], "private-learner-question", {}, "English", "JSS2")
    assert ask.call_count == 3
    assert [call.args[0] for call in sleep.call_args_list] == [1, 2]
    assert "private-provider-payload" not in caplog.text
    assert "private-learner-question" not in caplog.text
    assert "category=quota" in caplog.text


def test_other_errors_are_not_capacity_retried():
    with patch.object(tutor, "_ask", side_effect=RuntimeError("403 permission denied")) as ask, patch.object(tutor.time, "sleep") as sleep:
        with pytest.raises(RuntimeError):
            tutor._ask_with_capacity_retry(object(), [], "synthetic question", {}, "English", "JSS2")
    assert ask.call_count == 1
    sleep.assert_not_called()


@pytest.mark.parametrize("reply", [tutor.RATE_LIMIT_RESPONSE, tutor.TECHNICAL_FALLBACK_RESPONSE])
def test_provider_error_is_not_a_successful_classroom_lesson(reply):
    with pytest.raises(HTTPException) as caught:
        classroom_api._tutor_result(reply, 0.1, "synthetic")
    assert caught.value.status_code == 503
    assert caught.value.headers == {"Retry-After": "10"}


def test_successful_lesson_response_is_preserved():
    assert classroom_api._tutor_result("47 rounds to 50.", 0.1234, "synthetic") == {
        "reply": "47 rounds to 50.", "latency_seconds": 0.123, "learner_id": "synthetic"
    }


def test_chat_endpoint_signals_failure_instead_of_publishing_error_as_lesson():
    app = FastAPI()
    app.include_router(classroom_api.router)
    with patch.object(classroom_api, "_verify_session", return_value="synthetic"), patch.object(classroom_api, "_enforce_rate_limit"), patch.object(classroom_api, "get_tutor_reply", return_value=(tutor.RATE_LIMIT_RESPONSE, 0.1)):
        response = TestClient(app).post("/api/classroom/chat", json={"message":"synthetic question", "session_token":"x" * 30, "language":"English"})
    assert response.status_code == 503
    assert response.headers["retry-after"] == "10"
    assert "reply" not in response.json()
