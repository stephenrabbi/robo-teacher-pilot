"""Controlled tests for the V2.5 browser classroom API; no live services used."""
import base64
from unittest.mock import patch
from fastapi.testclient import TestClient

from v25_app import app
import classroom_api
import practice
from tutor import _language_instruction, get_tutor_reply

client = TestClient(app)


def test_practice_bank_covers_jss2_curriculum_strands():
    expected_topics = {
        'Whole Numbers', 'Fractions', 'Algebra', 'Ratio & Percentage',
        'Factors, Multiples & Roots', 'Decimals & Approximation', 'Directed Numbers',
        'Commercial Arithmetic', 'Inequalities & Graphs', 'Geometry & Mensuration',
        'Statistics & Probability',
    }
    assert set(practice.QUESTION_BANK) == expected_topics
    for levels in practice.QUESTION_BANK.values():
        assert set(levels) == {'Easy', 'Medium', 'Challenge'}
        assert all(len(questions) >= 2 for questions in levels.values())
        assert all('Step 1:' in item[3] for questions in levels.values() for item in questions)

    options = client.get('/api/classroom/practice/options')
    assert options.status_code == 200
    assert set(options.json()['topics']) == expected_topics


def test_practice_mode_marks_answers_and_tracks_score():
    session = client.post('/api/classroom/session').json()
    fixed = ("What is 2 + 3?", "Count on from 2.", "5", "2 + 3 = 5.")
    with patch.object(practice, '_choose_question', return_value=fixed):
        started = client.post('/api/classroom/practice/start', json={
            'session_token': session['session_token'], 'topic': 'Whole Numbers', 'difficulty': 'Easy'
        })
        assert started.status_code == 200
        assert started.json()['question'] == fixed[0]
        assert 'expected' not in started.json()

        marked = client.post('/api/classroom/practice/answer', json={
            'session_token': session['session_token'], 'answer': '5'
        })
        assert marked.status_code == 200
        assert marked.json()['correct'] is True
        assert marked.json()['message'] in practice.PRAISE_MESSAGES
        assert marked.json()['score'] == 1
        assert marked.json()['attempted'] == 1

        next_question = client.post('/api/classroom/practice/next', json={'session_token': session['session_token']})
        assert next_question.status_code == 200
        assert next_question.json()['question_number'] == 2
        assert next_question.json()['score'] == 1


def test_five_question_session_returns_final_results_and_missed_review():
    session = client.post('/api/classroom/session').json()
    fixed = ("What is 2 + 3?", "Count on from 2.", "5", "Step 1: Add 2 and 3.\nStep 2: The result is 5.")
    final_result = None
    with patch.object(practice, '_choose_question', return_value=fixed):
        started = client.post('/api/classroom/practice/start', json={
            'session_token': session['session_token'], 'topic': 'Whole Numbers',
            'difficulty': 'Easy', 'question_count': 5,
        })
        assert started.json()['total_questions'] == 5
        for index in range(5):
            final_result = client.post('/api/classroom/practice/answer', json={
                'session_token': session['session_token'], 'answer': '5' if index < 3 else '4'
            }).json()
            if index < 4:
                assert final_result['completed'] is False
                client.post('/api/classroom/practice/next', json={'session_token': session['session_token']})

    assert final_result['completed'] is True
    summary = final_result['summary']
    assert summary['score'] == 3
    assert summary['attempted'] == 5
    assert summary['percentage'] == 60
    assert len(summary['missed']) == 2
    assert summary['recommendation']
    blocked = client.post('/api/classroom/practice/next', json={'session_token': session['session_token']})
    assert blocked.status_code == 409


def test_practice_session_rejects_unsupported_question_count():
    session = client.post('/api/classroom/session').json()
    response = client.post('/api/classroom/practice/start', json={
        'session_token': session['session_token'], 'topic': 'Algebra',
        'difficulty': 'Easy', 'question_count': 7,
    })
    assert response.status_code == 422


def test_practice_mode_prevents_skipping_and_duplicate_marking():
    session = client.post('/api/classroom/session').json()
    client.post('/api/classroom/practice/start', json={
        'session_token': session['session_token'], 'topic': 'Fractions', 'difficulty': 'Medium'
    })
    skipped = client.post('/api/classroom/practice/next', json={'session_token': session['session_token']})
    assert skipped.status_code == 409
    client.post('/api/classroom/practice/answer', json={'session_token': session['session_token'], 'answer': 'wrong'})
    duplicate = client.post('/api/classroom/practice/answer', json={'session_token': session['session_token'], 'answer': 'wrong'})
    assert duplicate.status_code == 409


def test_incorrect_practice_answer_returns_teaching_steps():
    session = client.post('/api/classroom/session').json()
    fixed = ("What is 9 × 7?", "Think of equal groups.", "63", "Step 1: Use 9 groups of 7.\nStep 2: 9 × 7 = 63.")
    with patch.object(practice, '_choose_question', return_value=fixed):
        client.post('/api/classroom/practice/start', json={
            'session_token': session['session_token'], 'topic': 'Whole Numbers', 'difficulty': 'Easy'
        })
        marked = client.post('/api/classroom/practice/answer', json={
            'session_token': session['session_token'], 'answer': '50'
        })
    data = marked.json()
    assert data['correct'] is False
    assert data['message'].startswith('Good attempt')
    assert 'Step 1:' in data['explanation']
    assert 'Step 2:' in data['explanation']


def test_yoruba_deterministic_answer_uses_yoruba_number_word():
    reply, latency = get_tutor_reply("WEB-language-test", "2*3", "Yoruba")
    assert reply == "2*3 = 6\n\nÌdáhùn: Ẹ̀fà"
    assert latency == 0.0


def test_igbo_and_hausa_deterministic_answers_use_local_number_words():
    igbo_reply, _ = get_tutor_reply("WEB-igbo-test", "2*3", "Igbo")
    hausa_reply, _ = get_tutor_reply("WEB-hausa-test", "2*3", "Hausa")
    assert igbo_reply == "2*3 = 6\n\nAzịza: Isii"
    assert hausa_reply == "2*3 = 6\n\nAmsa: Shida"


def test_language_instructions_accept_typed_and_spoken_yoruba():
    automatic = _language_instruction("English")
    selected = _language_instruction("Yoruba")
    assert "current Maths question is in English or Yorùbá" in automatic
    assert "If it is in Yorùbá, reply entirely" in automatic
    assert "final-answer value as a Yorùbá number word" in automatic
    assert "may ask the Maths question in Yorùbá or English" in selected
    assert "reply entirely in clear, natural Yorùbá" in selected


def test_igbo_and_hausa_language_instructions_cover_text_and_voice():
    for language in ("Igbo", "Hausa"):
        instruction = _language_instruction(language)
        assert f"ask the Maths question in {language} or English" in instruction
        assert f"reply entirely in clear, natural {language}" in instruction


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
    assert tutor.call_args.args[2] == 'English'


def test_yoruba_language_reaches_all_classroom_tutoring_modes():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'get_tutor_reply', return_value=('Ìdáhùn ni 5.', 0.1)) as chat_tutor:
        chat = client.post('/api/classroom/chat', json={'message':'Kọ́ mi ní ìṣirò','session_token':session['session_token'],'language':'Yoruba'})
    assert chat.status_code == 200
    assert chat_tutor.call_args.args[2] == 'Yoruba'

    with patch.object(classroom_api, 'get_tutor_image_reply', return_value=('Àlàyé Yorùbá.', 0.1)) as image_tutor:
        image = client.post('/api/classroom/image', data={'session_token':session['session_token'],'language':'Yoruba'}, files={'image':('maths.png', b'fake-png', 'image/png')})
    assert image.status_code == 200
    assert image_tutor.call_args.args[4] == 'Yoruba'

    encoded = base64.b64encode(b'fake-png').decode()
    with patch.object(classroom_api, 'get_tutor_image_reply', return_value=('Àlàyé Yorùbá.', 0.1)) as board_tutor:
        board = client.post('/api/classroom/whiteboard', json={'session_token':session['session_token'],'image_data':f'data:image/png;base64,{encoded}','language':'Yoruba'})
    assert board.status_code == 200
    assert board_tutor.call_args.args[4] == 'Yoruba'

    with patch.object(classroom_api, 'get_tutor_audio_reply', return_value=('Àlàyé Yorùbá.', 0.1)) as audio_tutor:
        audio = client.post('/api/classroom/audio', data={'session_token':session['session_token'],'language':'Yoruba'}, files={'audio':('question.webm', b'fake-audio', 'audio/webm')})
    assert audio.status_code == 200
    assert audio_tutor.call_args.args[3] == 'Yoruba'


def test_classroom_rejects_unknown_language():
    session = client.post('/api/classroom/session').json()
    response = client.post('/api/classroom/chat', json={'message':'Explain fractions','session_token':session['session_token'],'language':'French'})
    assert response.status_code == 422


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
