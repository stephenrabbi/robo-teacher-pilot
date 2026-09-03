"""Controlled tests for the V2.5 browser classroom API; no live services used."""
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


if __name__ == '__main__':
    test_session_and_chat_use_pseudonymous_identity()
    test_tampered_session_is_rejected()
    test_question_length_is_bounded()
    test_provider_exception_is_sanitized()
    print('V2.5 classroom API safety tests passed.')
