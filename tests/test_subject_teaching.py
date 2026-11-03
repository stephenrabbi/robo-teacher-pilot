"""Subject teaching keeps session boundaries and never calls Maths mastery."""
from types import SimpleNamespace
from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient
from main import app
import classroom_api
import subject_tutor

client=TestClient(app)

@pytest.fixture
def question():
    session=client.post('/api/classroom/session').json()
    return dict(message='Explain nouns',subject='English Language',language='English',session_token=session['session_token'],conversation_id='a'*32)

def test_subject_routes_use_signed_class_and_keep_maths_provider_out(question):
    identity=classroom_api._verify_session(question['session_token'])
    classroom_api._classroom_profiles[identity]['class_level']='JSS3'
    with patch.object(subject_tutor,'teach',return_value=('A noun names something.',.1)) as teach, patch.object(classroom_api,'get_tutor_reply') as maths:
        response=client.post('/api/classroom/subject/chat',json=question)
        assert response.status_code==200
        assert teach.call_args.args[:6]==(identity,'English Language','English','JSS3','a'*32,'Explain nouns')
        maths.assert_not_called()

def test_subject_validation_and_auth_do_not_call_provider(question):
    with patch.object(subject_tutor,'teach') as teach:
        for change in [dict(subject='Mathematics'),dict(subject='Chemistry'),dict(language='French'),dict(message=' '),dict(message='x'*1201),dict(conversation_id='../other'),dict(class_level='JSS1')]:
            assert client.post('/api/classroom/subject/chat',json=question|change).status_code==422
        assert client.post('/api/classroom/subject/chat',json=question|dict(session_token='invalid-session-token-value')).status_code==401
        teach.assert_not_called()

def test_media_validates_size_type_and_passes_subject_context(question):
    form={k:v for k,v in question.items() if k!='message'}
    with patch.object(subject_tutor,'teach',return_value=('Plants need light.',.1)) as teach:
        response=client.post('/api/classroom/subject/image',data=form|dict(subject='Basic Science'),files={'file':('plant.png',b'educational image','image/png')})
        assert response.status_code==200
        assert teach.call_args.args[1]=='Basic Science'
        assert teach.call_args.args[-2:]==(b'educational image','image/png')
        response=client.post('/api/classroom/subject/audio',data=form,files={'file':('question.webm',b'educational recording','audio/webm')})
        assert response.status_code==200
        assert 'clarification' in teach.call_args.args[5]
        for payload,mime in [(b'','image/png'),(b'x'*(8*1024*1024+1),'image/png'),(b'bad','text/html')]:
            assert client.post('/api/classroom/subject/image',data=form,files={'file':('question',payload,mime)}).status_code in {415,422}
        assert teach.call_count==2

def test_provider_failure_returns_retry_message_without_private_detail(question):
    with patch.object(subject_tutor,'teach',side_effect=RuntimeError('private credential detail')):
        result=client.post('/api/classroom/subject/chat',json=question)
        assert result.status_code==503 and 'private' not in result.text

def test_followups_are_isolated_and_media_bytes_are_not_kept():
    subject_tutor._histories.clear()
    chat=Mock();chat.send_message.return_value=SimpleNamespace(text='A noun names a person, place or thing.')
    provider=Mock();provider.chats.create.return_value=chat
    with patch.object(subject_tutor.tutor,'_get_client',return_value=provider), patch.object(subject_tutor.tutor,'_safe_profile_update') as mastery:
        base=('learner-a','English Language','English','JSS2','a'*32)
        subject_tutor.teach(*base,'Explain nouns')
        subject_tutor.teach(*base,'Give another example')
        assert len(provider.chats.create.call_args.kwargs['history'])==2
        for other in [('learner-b',*base[1:]),(base[0],'Basic Science',*base[2:]),(*base[:2],'Yoruba',*base[3:]),(*base[:3],'JSS1',base[4]),(*base[:4],'b'*32)]:
            subject_tutor.teach(*other,'New question')
            assert provider.chats.create.call_args.kwargs['history']==[]
        subject_tutor.teach(*base,'Describe this',b'private-image-bytes','image/png')
        history=subject_tutor._history(base)
        assert all(part.inline_data is None for entry in history for part in entry.parts)
        assert 'private-image-bytes' not in str(history)
        mastery.assert_not_called()

def test_history_is_bounded_and_expires():
    subject_tutor._histories.clear()
    with patch.object(subject_tutor,'_MAX_CONVERSATIONS',2):
        for key in ['a','b','c']: subject_tutor._remember(key,list(range(30)))
        assert subject_tutor._history('a')==[]
        assert subject_tutor._history('c')==list(range(18,30))
        with patch.object(subject_tutor.time,'monotonic',return_value=10**12):
            assert subject_tutor._history('c')==[]

def test_subject_instructions_keep_language_and_science_boundaries():
    english=subject_tutor.subject_instruction('English Language','Yoruba','JSS1')
    assert 'Preserve English example sentences' in english and 'Yorùbá' in english
    science=subject_tutor.subject_instruction('Basic Science','English','JSS3')
    for rule in ['hazardous experimental procedures','never guess unclear words','Never identify people','not a claim of complete syllabus']:
        assert rule in science
    with pytest.raises(ValueError):subject_tutor.subject_instruction('Chemistry','English','JSS2')
