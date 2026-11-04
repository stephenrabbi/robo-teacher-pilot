from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from v25_app import app
import classroom_api
import tutor
from topic_video_context import video_question_reference

client = TestClient(app)

def test_fraction_addition_video_is_selected_without_replacing_other_fraction_media():
    for lesson in ['Add 1/2 + 1/3.', 'Adding fractions with different denominators.', 'Three sixths plus two sixths.', 'Add the fractions. Multiply each numerator and denominator to make sixths.']:
        media=tutor.select_lesson_media(lesson, 'English')
        assert media['kind']=='video' and media['video_id']=='adding-unlike-fractions'
    for lesson in ['Subtract fractions.', 'Multiply 1/2 and 1/3.', 'What is a numerator?']:
        assert tutor.select_lesson_media(lesson, 'English').get('video_id')!='adding-unlike-fractions'
    assert tutor.select_lesson_media('Add fractions.', 'Yoruba').get('video_id')!='adding-unlike-fractions'

def test_fractions_video_context_uses_own_captions_and_is_allowed_for_text_and_audio():
    reference=video_question_reference('adding-unlike-fractions', 24)
    assert 'one third' in reference.lower() and 'two sixths' in reference
    assert 'Paused position: 54.24 seconds' in video_question_reference('adding-unlike-fractions', 999)
    session=token()
    with patch.object(classroom_api, 'get_tutor_reply', return_value=('Explanation', .1)) as provider:
        result=client.post('/api/classroom/chat', json={'message':'Why are the pieces sixths?', 'session_token':session, 'video_context':{'id':'adding-unlike-fractions','time':24}})
        assert result.status_code==200
        assert 'Adding unlike fractions' in provider.call_args.args[1]
    with patch.object(classroom_api, 'get_tutor_audio_reply', return_value=('Explanation', .1)) as provider:
        result=client.post('/api/classroom/audio', data={'session_token':session,'video_id':'adding-unlike-fractions','video_time':'24'}, files={'audio':('question.webm',b'synthetic voice','audio/webm')})
        assert result.status_code==200
        assert 'two sixths' in provider.call_args.kwargs['reference_context']

def token():
    return client.post('/api/classroom/session').json()['session_token']

def test_reference_uses_own_transcript_and_captions_near_the_paused_time():
    reference = video_question_reference('rounding-nearest-ten', 14)
    assert 'Paused position: 14.00 seconds' in reference
    assert 'Nearby captions:' in reference and 'is forty five.' in reference
    assert 'Complete transcript:' in reference and 'units digit of five or more' in reference
    assert 'never be used to guess an unclear spoken number' in reference
    assert 'Paused position: 41.09 seconds' in video_question_reference('rounding-nearest-ten', 900)
    for video_id, time in [('https://example.com/x', 2), ('../secret', 2), ('rounding-nearest-ten', -1), ('rounding-nearest-ten', float('nan'))]:
        with pytest.raises(ValueError):
            video_question_reference(video_id, time)

def test_text_video_question_gets_server_reference_but_plain_question_is_unchanged():
    session = token()
    with patch.object(classroom_api, 'get_tutor_reply', return_value=('Explanation', .1)) as provider:
        response = client.post('/api/classroom/chat', json={'message':'Why did she say that?', 'session_token':session, 'video_context':{'id':'rounding-nearest-ten','time':14}})
        assert response.status_code == 200
        message = provider.call_args.args[1]
        assert message.startswith('Why did she say that?') and 'Complete transcript:' in message and 'is forty five.' in message
        client.post('/api/classroom/chat', json={'message':'A plain question', 'session_token':session})
        assert provider.call_args.args[1] == 'A plain question'

def test_video_context_rejects_unknown_ids_times_and_supplied_transcripts():
    session = token()
    with patch.object(classroom_api, 'get_tutor_reply') as provider:
        for context in [{'id':'../secret','time':2}, {'id':'rounding-nearest-ten','time':-1}, {'id':'rounding-nearest-ten','time':'nan'}, {'id':'rounding-nearest-ten','time':2,'transcript':'forged'}]:
            assert client.post('/api/classroom/chat', json={'message':'Question', 'session_token':session,'video_context':context}).status_code == 422
        provider.assert_not_called()

def test_audio_video_question_uses_same_reference_and_requires_id_time_pair():
    session = token()
    recording = {'audio':('question.webm', b'synthetic voice bytes', 'audio/webm')}
    with patch.object(classroom_api, 'get_tutor_audio_reply', return_value=('Explanation', .1)) as provider:
        response = client.post('/api/classroom/audio', data={'session_token':session,'video_id':'rounding-nearest-ten','video_time':'14'}, files=recording)
        assert response.status_code == 200
        assert 'Complete transcript:' in provider.call_args.kwargs['reference_context']
        assert client.post('/api/classroom/audio',data={'session_token':session,'video_id':'rounding-nearest-ten'},files=recording).status_code == 422
        assert client.post('/api/classroom/audio',data={'session_token':session,'video_id':'../secret','video_time':'14'},files=recording).status_code == 422
        assert provider.call_count == 1

def test_audio_reference_does_not_replace_transcription_safety_rules():
    reference = video_question_reference('rounding-nearest-ten', 14)
    with patch.object(tutor, '_media_reply', return_value=('Reply', .1)) as provider:
        tutor.get_tutor_audio_reply('synthetic', b'voice', 'audio/webm', reference_context=reference)
        prompt = provider.call_args.args[3]
        assert 'DO NOT solve the problem' in prompt and 'Do not infer a number' in prompt
        assert 'Complete transcript:' in prompt and 'never be used to guess an unclear spoken number' in prompt
