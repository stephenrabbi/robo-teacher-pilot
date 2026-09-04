"""Controlled tests for the V2.5 browser classroom API; no live services used."""
import base64
from unittest.mock import patch
from fastapi.testclient import TestClient

from v25_app import app
import classroom_api

client = TestClient(app)


def test_session_and_chat_use_pseudonymous_identity():
    session = client.post('/api/classroom/session')
    assert session.status_code == 200
    data = session.json()
    assert data['learner_id'].startswith('WEB-')
    assert 'session_token' in data
    with patch.object(classroom_api, 'get_tutor_reply', return_value=('Step 1: Find a common denominator.\nFinal answer: 5/6', 0.12)) as tutor:
        response = client.post('/api/classroom/chat', json={'message':'Teach me 2/3 + 1/6','session_token':data['session_token']})
    assert response.status_code == 200
    assert 'common denominator' in response.json()['reply']
    assert tutor.call_args.args[0] == data['learner_id']


def test_tampered_session_is_rejected():
    session = client.post('/api/classroom/session').json()
    bad = session['session_token'][:-1] + ('0' if session['session_token'][-1] != '0' else '1')
    response = client.post('/api/classroom/chat', json={'message':'Explain ratio','session_token':bad})
    assert response.status_code == 401


def test_question_length_is_bounded():
    session = client.post('/api/classroom/session').json()
    response = client.post('/api/classroom/chat', json={'message':'x'*1201,'session_token':session['session_token']})
    assert response.status_code == 422


def test_provider_exception_is_sanitized():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'get_tutor_reply', side_effect=RuntimeError('secret provider detail')):
        response = client.post('/api/classroom/chat', json={'message':'Explain fractions','session_token':session['session_token']})
    assert response.status_code == 503
    assert 'secret provider detail' not in response.text


def test_classroom_image_uses_same_pseudonymous_identity():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'get_tutor_image_reply', return_value=('The image shows 2 + 3. Final answer: 5', 0.2)) as tutor:
        response = client.post('/api/classroom/image', data={'session_token':session['session_token'], 'caption':'Explain this'}, files={'image':('maths.png', b'fake-png', 'image/png')})
    assert response.status_code == 200
    assert response.json()['reply'].endswith('5')
    assert tutor.call_args.args[0] == session['learner_id']


def test_classroom_image_rejects_unsupported_type():
    session = client.post('/api/classroom/session').json()
    response = client.post('/api/classroom/image', data={'session_token':session['session_token']}, files={'image':('notes.txt', b'not-an-image', 'text/plain')})
    assert response.status_code == 415


def test_classroom_image_rejects_oversized_file():
    session = client.post('/api/classroom/session').json()
    oversized = b'x' * (classroom_api.MAX_IMAGE_BYTES + 1)
    response = client.post('/api/classroom/image', data={'session_token':session['session_token']}, files={'image':('large.jpg', oversized, 'image/jpeg')})
    assert response.status_code == 413


def test_classroom_whiteboard_uses_json_canvas_and_pseudonymous_identity():
    session = client.post('/api/classroom/session').json()
    encoded = base64.b64encode(b'fake-png').decode()
    with patch.object(classroom_api, 'get_tutor_image_reply', return_value=('Two times seven is 14.', 0.2)) as tutor:
        response = client.post('/api/classroom/whiteboard', json={
            'session_token': session['session_token'],
            'image_data': f'data:image/png;base64,{encoded}',
            'caption': 'Explain my working',
        })
    assert response.status_code == 200
    assert response.json()['reply'].endswith('14.')
    assert tutor.call_args.args[:4] == (session['learner_id'], b'fake-png', 'image/png', 'Explain my working')


def test_classroom_whiteboard_rejects_invalid_data():
    session = client.post('/api/classroom/session').json()
    response = client.post('/api/classroom/whiteboard', json={
        'session_token': session['session_token'],
        'image_data': 'data:image/png;base64,this-is-not-base64!',
    })
    assert response.status_code == 422


def test_classroom_audio_uses_same_pseudonymous_identity():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'get_tutor_audio_reply', return_value=('Subtract 4, then divide by 2. Final answer: 6', 0.3)) as tutor:
        response = client.post('/api/classroom/audio', data={'session_token':session['session_token']}, files={'audio':('question.webm', b'fake-audio', 'audio/webm;codecs=opus')})
    assert response.status_code == 200
    assert response.json()['reply'].endswith('6')
    assert tutor.call_args.args[0] == session['learner_id']


def test_classroom_audio_rejects_unsupported_type():
    session = client.post('/api/classroom/session').json()
    response = client.post('/api/classroom/audio', data={'session_token':session['session_token']}, files={'audio':('question.txt', b'not-audio', 'text/plain')})
    assert response.status_code == 415


def test_classroom_audio_rejects_oversized_file():
    session = client.post('/api/classroom/session').json()
    oversized = b'x' * (classroom_api.MAX_AUDIO_BYTES + 1)
    response = client.post('/api/classroom/audio', data={'session_token':session['session_token']}, files={'audio':('large.webm', oversized, 'audio/webm')})
    assert response.status_code == 413


if __name__ == '__main__':
    test_session_and_chat_use_pseudonymous_identity()
    test_tampered_session_is_rejected()
    test_question_length_is_bounded()
    test_provider_exception_is_sanitized()
    test_classroom_image_uses_same_pseudonymous_identity()
    test_classroom_image_rejects_unsupported_type()
    test_classroom_image_rejects_oversized_file()
    test_classroom_audio_uses_same_pseudonymous_identity()
    test_classroom_audio_rejects_unsupported_type()
    test_classroom_audio_rejects_oversized_file()
    print('V2.5 classroom API safety tests passed.')
