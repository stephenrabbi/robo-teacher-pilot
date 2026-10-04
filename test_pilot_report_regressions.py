"""Reproduce answer-entry failures and Safari audio-format rejection."""
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from main import app
import practice
import classroom_api

client = TestClient(app)

@pytest.mark.parametrize('value, expected', [('x = 8','8'),(' X = 8 ','8'),('1 / 2','1/2'),('6 / 12','1/2'),('2 : 3','2:3')])
def test_valid_phone_answer_spacing(value, expected):
    assert practice._normalise_answer(value) == expected

@pytest.mark.parametrize('value', ['2:0','a:b','2:3:4',':','1/0'])
def test_invalid_answer_does_not_freeze_practice(value):
    session = client.post('/api/classroom/session',json={'nickname':'Synthetic Tester'}).json()
    token=session['session_token']
    started=client.post('/api/classroom/practice/start',json={'session_token':token,'topic':'Fractions','difficulty':'Easy'} )
    assert started.status_code == 200
    response=client.post('/api/classroom/practice/answer',json={'session_token':token,'answer':value})
    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert client.post('/api/classroom/practice/next',json={'session_token':token}).status_code == 200

def test_safari_mp4_audio_reaches_tutoring_provider():
    token=client.post('/api/classroom/session',json={'nickname':'Synthetic Tester'}).json()['session_token']
    with patch.object(classroom_api,'get_tutor_audio_reply',return_value=('Three quarters',0.2)) as reply:
        response=client.post('/api/classroom/audio',data={'session_token':token,'language':'English'},files={'audio':('question.m4a',b'synthetic-audio-container','audio/mp4;codecs=mp4a.40.2')})
    assert response.status_code == 200
    assert reply.call_args.args[2] == 'audio/mp4'
    source=(Path(__file__).parent/'classroom'/'app.js').read_text()
    assert "'audio/mp4'" in source
    assert "type.includes('mp4')?'m4a'" in source
