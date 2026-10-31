from unittest.mock import patch
import pytest
import cloud_ai_provider as provider


def test_default_keeps_developer_route_even_with_ambient_cloud_switch():
    with patch.dict('os.environ', {'GEMINI_API_KEY':'synthetic-key','GOOGLE_GENAI_USE_VERTEXAI':'true'}, clear=True), patch.object(provider.genai,'Client') as client:
        provider.create_ai_client()
        client.assert_called_once_with(enterprise=False,vertexai=False,api_key='synthetic-key')


def test_vertex_uses_explicit_project_region_and_no_developer_key():
    config={'ROBO_AI_PROVIDER':'vertex','GOOGLE_CLOUD_PROJECT':'synthetic-project','GOOGLE_CLOUD_LOCATION':'global','GEMINI_MODEL':'reviewed-text-model','GEMINI_TTS_MODEL':'reviewed-tts-model','GEMINI_STREAMING_TTS_MODEL':'reviewed-stream-model','GEMINI_API_KEY':'must-not-be-forwarded'}
    with patch.dict('os.environ',config,clear=True),patch.object(provider.genai,'Client') as client:
        provider.create_ai_client()
        client.assert_called_once_with(enterprise=True,vertexai=True,project='synthetic-project',location='global')


def test_incomplete_cloud_config_fails_before_sdk_or_fallback():
    with patch.dict('os.environ',{'ROBO_AI_PROVIDER':'vertex','GEMINI_API_KEY':'no-fallback'},clear=True),patch.object(provider.genai,'Client') as client:
        with pytest.raises(ValueError,match='GOOGLE_CLOUD_PROJECT'):
            provider.create_ai_client()
        client.assert_not_called()


def test_unknown_provider_fails_before_sdk():
    with patch.dict('os.environ',{'ROBO_AI_PROVIDER':'typo'},clear=True),patch.object(provider.genai,'Client') as client:
        with pytest.raises(ValueError,match='developer or vertex'):
            provider.create_ai_client()
        client.assert_not_called()
