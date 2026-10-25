"""Synthetic offline identity checks. Never connect to production storage."""
from unittest.mock import patch

import pytest
from fastapi import HTTPException

import classroom_api
import practice_progress


def issue(key="a" * 48, code="IND-SYNTHETIC", signing_key=b"before-restart"):
    with patch.dict("os.environ", {"CLASSROOM_IDENTITY_MODE": "device-key-v2"}), \
         patch.object(classroom_api, "_SESSION_KEY", signing_key):
        return classroom_api._new_session(key, code)


def test_legacy_identity_changes_when_unconfigured_signing_key_changes():
    with patch.dict("os.environ", {"CLASSROOM_IDENTITY_MODE": "legacy"}):
        with patch.object(classroom_api, "_SESSION_KEY", b"boot-one"):
            first, _ = classroom_api._new_session("a" * 48, "IND-SYNTHETIC")
        with patch.object(classroom_api, "_SESSION_KEY", b"boot-two"):
            second, _ = classroom_api._new_session("a" * 48, "IND-SYNTHETIC")
    assert first != second


def test_v2_identity_survives_signing_key_rotation_but_old_token_does_not():
    first, old_token = issue()
    second, new_token = issue(signing_key=b"after-restart")
    assert first == second
    with patch.object(classroom_api, "_SESSION_KEY", b"after-restart"):
        assert classroom_api._verify_session(new_token) == first
        with pytest.raises(HTTPException) as error:
            classroom_api._verify_session(old_token)
        assert error.value.status_code == 401


def test_v2_code_and_nickname_are_not_cross_device_credentials():
    owner, _ = issue()
    other, _ = issue(key="b" * 48)
    anonymous, _ = issue(key=None)
    another_anonymous, _ = issue(key=None)
    assert len({owner, other, anonymous, another_anonymous}) == 4


def test_v2_code_is_normalized_and_profiles_remain_separate():
    first, token = issue(code="ind-synthetic")
    same, _ = issue()
    other, _ = issue(code="IND-ANOTHER")
    assert first == same
    assert first != other
    assert "a" * 48 not in token
    assert "IND-SYNTHETIC" not in token


def test_v2_retrieves_durable_owned_records_after_process_cache_reset():
    owner, _ = issue()
    row = {"learner_id": owner, "session_id": "synthetic-result"}
    # This fake durable store is outside the cleared process-memory cache.
    durable = {owner: [row]}
    with patch.object(practice_progress, "_sheet_configured", return_value=True), \
         patch.object(practice_progress, "_sheet_records", side_effect=lambda uid: durable.get(uid, [])), \
         patch.object(practice_progress, "_memory_records", []):
        returned, _ = issue(signing_key=b"after-restart")
        rows, synced = practice_progress.get_records(returned)
        assert synced and rows == [row]
        stranger, _ = issue(key="b" * 48)
        assert practice_progress.get_records(stranger) == ([], True)


def test_unknown_identity_mode_fails_closed():
    with patch.dict("os.environ", {"CLASSROOM_IDENTITY_MODE": "typo"}):
        with pytest.raises(HTTPException) as error:
            classroom_api._new_session("a" * 48, "IND-SYNTHETIC")
    assert error.value.status_code == 503


def test_default_identity_mode_preserves_existing_legacy_namespace():
    with patch.dict("os.environ", {}, clear=True), \
         patch.object(classroom_api, "_SESSION_KEY", b"existing-persistent-key"):
        default, _ = classroom_api._new_session("a" * 48, "IND-SYNTHETIC")
        with patch.dict("os.environ", {"CLASSROOM_IDENTITY_MODE": "legacy"}):
            legacy, _ = classroom_api._new_session("a" * 48, "IND-SYNTHETIC")
    assert default == legacy
    assert not default.startswith("WEB-V2-")
