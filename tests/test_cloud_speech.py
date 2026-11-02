from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
import pytest
import tutor
from cloud_ai_provider import stream_cloud_speech


def response(data=None, mime='audio/L16;codec=pcm;rate=24000'):
    part = NS(inline_data=NS(data=data, mime_type=mime) if data else None)
    return NS(candidates=[NS(content=NS(parts=[part]))])


@pytest.mark.parametrize('mime', ['audio/L16;codec=pcm;rate=24000', 'audio/l16; rate=24000; channels=1'])
def test_cloud_audio_stream_skips_metadata_and_preserves_chunk_order(mime):
    client = Mock()
    client.models.generate_content_stream.return_value = iter([
        NS(candidates=None), response(), response(b'\x00\x01', mime), response(b'\x02\x03', mime)])
    assert list(stream_cloud_speech(client, 'cloud-tts', 'hello', 'Kore')) == [b'\x00\x01', b'\x02\x03']
    args = client.models.generate_content_stream.call_args.kwargs
    assert args['model'] == 'cloud-tts'
    assert args['config'].speech_config.voice_config.prebuilt_voice_config.voice_name == 'Kore'
    client.interactions.create.assert_not_called()


@pytest.mark.parametrize('mime', ['audio/wav', 'audio/L16;rate=16000', 'audio/mpeg'])
def test_cloud_stream_rejects_audio_that_browser_would_decode_incorrectly(mime):
    client = Mock()
    client.models.generate_content_stream.return_value = [response(b'bad-format', mime)]
    with pytest.raises(ValueError, match='unsupported PCM'):
        list(stream_cloud_speech(client, 'cloud-tts', 'hello', 'Kore'))


def test_cloud_empty_audio_fails_for_existing_route_fallback():
    client = Mock()
    client.models.generate_content_stream.return_value = [NS(candidates=[])]
    with pytest.raises(RuntimeError, match='no audio'):
        list(stream_cloud_speech(client, 'cloud-tts', 'hello', 'Kore'))


def test_tutor_cloud_selection_bypasses_developer_interactions():
    client = Mock()
    with patch.dict('os.environ', {'ROBO_AI_PROVIDER': 'vertex'}), patch.object(tutor, '_get_client', return_value=client), patch.object(tutor, 'stream_cloud_speech', return_value=iter([b'pcm'])) as speech:
        assert list(tutor.stream_tutor_speech('One plus one is two.')) == [b'pcm']
    assert 'TRANSCRIPT:' in speech.call_args.args[2]
    client.interactions.create.assert_not_called()
