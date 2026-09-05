"""Controlled tests for the V2.5 browser classroom API; no live services used."""
import base64
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from v25_app import app
import classroom_api
import practice
import practice_progress
from tutor import GEMINI_STREAMING_TTS_MODEL, GEMINI_TTS_MODEL, TTS_VOICES, _language_instruction, _pcm_to_wav, _prepare_spoken_transcript, _speech_chunks, _spoken_excerpt, get_tutor_reply

client = TestClient(app)
PROJECT_ROOT = Path(__file__).parent


def test_mobile_classroom_keeps_teacher_compact_and_touch_targets_accessible():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    css = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert '20260905-practiceclass1' in html
    assert 'id="learnerNickname"' in html
    assert 'id="learnerClass"' in html
    assert "learnerNickname.value=''" in script
    assert "localStorage.setItem('roboTeacherProfiles'" in script
    assert 'id="showTeacherLogin"' in html
    assert 'id="teacherAccessKey" type="password"' in html
    assert 'id="changeLearner"' in html
    assert 'id="teacherClass"' in html
    assert 'id="downloadTeacherReport"' in html
    assert 'downloadTeacherDashboardReport' in script
    assert 'id="practiceClass"' in html
    assert 'id="practiceClassSummary"' in html
    assert "class_level:practiceClass.value" in script
    assert "data.class_level} · ${data.topic}" in script
    assert 'Continue Learning →' in html
    assert 'id="weeklyImprovement"' in html
    assert "practiceRequest('progress',{class_level:learnerClass.value})" in script
    assert 'id="teacherDashboardButton"' in html
    assert "fetch('/api/classroom/teacher/dashboard'" in script
    assert 'id="readAnswer"' in html
    assert 'aria-expanded="true"' in html
    assert '@media(max-width:600px)' in css
    assert '.teacher-panel{grid-template-columns:82px 1fr' in css
    assert '.founder-avatar{height:205px!important}' in css
    assert 'min-height:44px' in css
    assert 'void speakText(data.reply)' in script
    assert 'stopTeacherAudio();\n    await ensureSession();' in script
    assert 'data-voice-gender="female"' in html
    assert 'prepareSpeechText(text)' in script
    assert "fetch('/api/classroom/speech'" in script
    assert "voice_gender:teacherPanel.dataset.voiceGender" in script
    assert 'speechSynthesis' not in script
    assert 'teacherSpeechController.abort()' in script
    assert "error.name==='AbortError'" in script
    assert 'response.body.getReader()' in script
    assert 'createBuffer(1,samples,24000)' in script


def test_pcm_audio_is_wrapped_as_playable_wav():
    wav_audio = _pcm_to_wav(b'\x00\x00' * 240)
    assert wav_audio.startswith(b'RIFF')
    assert b'WAVE' in wav_audio[:16]


def test_avatar_genders_use_distinct_gemini_voices():
    assert TTS_VOICES == {'female': 'Aoede', 'male': 'Charon'}
    assert GEMINI_TTS_MODEL == 'gemini-2.5-flash-preview-tts'
    assert GEMINI_STREAMING_TTS_MODEL == 'gemini-3.1-flash-tts-preview'


def test_yoruba_speech_localizes_numbers_and_maths_operators():
    spoken = _prepare_spoken_transcript('2 × 3 = 6. Then 20 + 5 = 25.', 'Yoruba')
    assert spoken == 'Méjì times Mẹ́ta jẹ́ Mẹ́fà. Then Ogún plus Márùn-ún jẹ́ Ẹ̀ẹ́dọ́gbọ̀n.'
    assert not any(character.isdigit() for character in spoken)
    decimal = _prepare_spoken_transcript('2.5 + 1 = 3.5', 'Yoruba')
    assert decimal == 'Méjì point Márùn-ún plus Ọ̀kan jẹ́ Mẹ́ta point Márùn-ún'
    larger = _prepare_spoken_transcript('127 + 1,000', 'Yoruba')
    assert larger == 'Ọ̀kan Méjì Méje plus Ọ̀kan Odo Odo Odo'
    assert not any(character.isdigit() for character in larger)
    assert _prepare_spoken_transcript('2 + 3 = 5', 'English') == '2 + 3 = 5'


def test_igbo_speech_localizes_numbers_and_maths_operators():
    spoken = _prepare_spoken_transcript('2 × 3 = 6. Then 20 + 5 = 25.', 'Igbo')
    assert spoken == 'Abụọ ugboro Atọ ha nhata Isii. Then Iri abụọ gbakwunyere Ise ha nhata Iri abụọ na ise.'
    assert not any(character.isdigit() for character in spoken)
    assert _prepare_spoken_transcript('2.5 ÷ 1', 'Igbo') == 'Abụọ ntụpọ Ise kewaa site na Otu'


def test_hausa_speech_localizes_numbers_and_maths_operators():
    spoken = _prepare_spoken_transcript('2 × 3 = 6. Then 20 + 5 = 25.', 'Hausa')
    assert spoken == 'Biyu sau Uku daidai yake da Shida. Then Ashirin da Biyar daidai yake da Ashirin da biyar.'
    assert not any(character.isdigit() for character in spoken)
    assert _prepare_spoken_transcript('2.5 ÷ 1', 'Hausa') == 'Biyu ɗigo Biyar raba da Ɗaya'


def test_long_speech_is_split_into_short_voice_consistent_chunks():
    chunks = _speech_chunks(('This is a complete teaching sentence. ' * 80).strip())
    assert len(chunks) > 1
    assert all(len(chunk) <= 700 for chunk in chunks)
    excerpt = _spoken_excerpt(('This sentence should be spoken naturally. ' * 40).strip())
    assert len(excerpt) <= 650
    assert excerpt.endswith('.')


def test_natural_speech_endpoint_uses_female_avatar_voice():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'stream_tutor_speech', return_value=iter([b'pcm-', b'audio'])) as tts:
        response = client.post('/api/classroom/speech', json={
            'text': 'Let us solve this carefully.',
            'session_token': session['session_token'],
            'language': 'English',
            'voice_gender': 'female',
        })
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('audio/l16')
    assert response.content == b'pcm-audio'
    assert tts.call_args.args[1:] == ('English', 'female')


def test_speech_playback_does_not_consume_the_tutor_question_limit():
    classroom_api._request_times.clear()
    session = client.post('/api/classroom/session').json()
    learner_id = session['learner_id']
    for _ in range(classroom_api._RATE_MAX_REQUESTS):
        classroom_api._enforce_rate_limit(learner_id)
    with patch.object(classroom_api, 'stream_tutor_speech', return_value=iter([b'audio'])):
        response = client.post('/api/classroom/speech', json={
            'text': 'The answer is six.',
            'session_token': session['session_token'],
            'language': 'English',
            'voice_gender': 'female',
        })
    assert response.status_code == 200
    assert response.content == b'audio'
    assert len(classroom_api._request_times[f'speech:{learner_id}']) == 1


def test_stable_anonymous_key_restores_progress_without_exposing_identity():
    practice_progress._reset_for_tests()
    learner_key = 'a' * 48
    first = client.post('/api/classroom/session', json={'learner_key': learner_key}).json()
    second = client.post('/api/classroom/session', json={'learner_key': learner_key}).json()
    other = client.post('/api/classroom/session', json={'learner_key': 'b' * 48}).json()
    assert first['learner_id'] == second['learner_id']
    assert first['learner_id'] != other['learner_id']
    assert learner_key not in first['session_token']
    fixed = ("What is 2 + 3?", "Count on from 2.", "5", "Step 1: Add 2 and 3.\nStep 2: The result is 5.")
    with patch.object(practice, '_build_question_queue', return_value=[fixed] * 5):
        client.post('/api/classroom/practice/start', json={
            'session_token': first['session_token'], 'topic': 'Whole Numbers',
            'difficulty': 'Easy', 'question_count': 5,
        })
        for index in range(5):
            marked = client.post('/api/classroom/practice/answer', json={
                'session_token': first['session_token'], 'answer': '5' if index < 4 else '4',
            })
            assert marked.status_code == 200
            if index < 4:
                client.post('/api/classroom/practice/next', json={'session_token': first['session_token']})

    dashboard = client.post('/api/classroom/practice/progress', json={
        'session_token': second['session_token'],
    })
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert data['sessions'] == 1
    assert data['total_questions'] == 5
    assert data['total_correct'] == 4
    assert data['average_percentage'] == 80
    assert data['strongest_topic'] == 'Standard Form'
    assert data['recommended_term'] == 'First Term'
    assert data['recent_sessions'][0]['percentage'] == 80

    empty = client.post('/api/classroom/practice/progress', json={
        'session_token': other['session_token'],
    }).json()
    assert empty['sessions'] == 0
    assert empty['recent_sessions'] == []
    assert [term['term'] for term in empty['learning_path']] == ['First Term', 'Second Term', 'Third Term']
    assert empty['learning_path'][0]['topics'][0]['status'] == 'recommended'


def test_progress_is_class_aware_and_adjusts_repeated_performance():
    practice_progress._reset_for_tests()
    now = __import__('datetime').datetime.now(__import__('datetime').UTC)
    base = {
        'learner_id': 'WEB-adaptive', 'topic': 'Algebra', 'difficulty': 'Medium',
        'attempted': 5, 'class_level': 'JSS3',
    }
    for index, score in enumerate((2, 1)):
        practice_progress._memory_records.append({
            **base, 'session_id': f'low-{index}', 'score': score,
            'percentage': score * 20, 'timestamp': (now - __import__('datetime').timedelta(days=index)).isoformat(),
        })
    practice_progress._memory_records.append({
        **base, 'class_level': 'JSS2', 'session_id': 'other-class', 'score': 5,
        'percentage': 100, 'timestamp': now.isoformat(),
    })
    dashboard = practice_progress.build_dashboard('WEB-adaptive', 'JSS3')
    assert dashboard['sessions'] == 2
    assert dashboard['recommended_topic'] == 'Factorisation & Quadratic Expressions'
    assert dashboard['recommended_term'] == 'First Term'
    assert dashboard['recommended_difficulty'] == 'Easy'
    assert dashboard['weekly_summary']['questions'] == 10


def test_consistent_success_moves_the_learner_up_one_level():
    practice_progress._reset_for_tests()
    now = __import__('datetime').datetime.now(__import__('datetime').UTC).isoformat()
    for index in range(2):
        practice_progress._memory_records.append({
            'learner_id': 'WEB-strong', 'class_level': 'JSS1', 'session_id': f'high-{index}',
            'topic': 'Fractions', 'difficulty': 'Easy', 'score': 5, 'attempted': 5,
            'percentage': 100, 'timestamp': now,
        })
    dashboard = practice_progress.build_dashboard('WEB-strong', 'JSS1')
    assert dashboard['recommended_difficulty'] == 'Medium'
    fraction = next(item for term in dashboard['learning_path'] for item in term['topics'] if item['topic'] == 'Fractions')
    assert fraction['status'] == 'recommended'
    assert fraction['percentage'] == 100


def test_teacher_dashboard_returns_aggregates_without_identities():
    practice_progress._reset_for_tests()
    practice_progress._memory_records.append({
        'learner_id': 'WEB-private', 'class_level': 'JSS2', 'session_id': 'aggregate-1',
        'topic': 'Simple Equations', 'difficulty': 'Easy', 'score': 4, 'attempted': 5,
        'percentage': 80, 'timestamp': '2026-09-05T10:00:00+00:00',
    })
    dashboard = practice_progress.build_teacher_dashboard('JSS2')
    assert dashboard['learners'] == 1
    assert dashboard['average_percentage'] == 80
    assert dashboard['strongest_topic'] == 'Simple Equations'
    assert dashboard['weakest_topic'] == 'Simple Equations'
    assert dashboard['recommendation']
    assert len(dashboard['weekly_trend']) == 6
    assert 'learner_id' not in dashboard
    assert 'recent_sessions' not in dashboard


def test_existing_eight_column_progress_sheet_is_extended_for_class_level():
    class Worksheet:
        col_count = 8
        def row_values(self, row): return practice_progress._HEADER[:-1]
        def add_cols(self, count): self.col_count += count
        def update_cell(self, row, column, value): self.updated = (row, column, value)
    worksheet = Worksheet()
    spreadsheet = type('Spreadsheet', (), {'worksheet': lambda self, title: worksheet})()
    client = type('Client', (), {'open_by_key': lambda self, key: spreadsheet})()
    practice_progress._reset_for_tests()
    practice_progress._client = client
    with patch.dict('os.environ', {'GOOGLE_SHEET_ID': 'sheet', 'GOOGLE_SERVICE_ACCOUNT_JSON': '{}'}):
        assert practice_progress._get_worksheet() is worksheet
    assert worksheet.col_count == 9
    assert worksheet.updated == (1, 9, 'Class Level')


def test_classroom_session_accepts_a_safe_nickname_and_class_level():
    response = client.post('/api/classroom/session', json={
        'learner_key': 'c' * 48, 'nickname': 'Tobi', 'class_level': 'JSS1',
    })
    assert response.status_code == 200
    assert response.json()['nickname'] == 'Tobi'
    assert response.json()['class_level'] == 'JSS1'
    unsafe = client.post('/api/classroom/session', json={
        'learner_key': 'c' * 48, 'nickname': '<script>', 'class_level': 'JSS4',
    })
    assert unsafe.status_code == 422


def test_practice_options_expose_class_and_term_curriculum():
    options = client.get('/api/classroom/practice/options')
    assert options.status_code == 200
    data = options.json()
    assert set(data['topics_by_class']) == {'JSS1', 'JSS2', 'JSS3'}
    assert set(data['curriculum']['JSS1']) == {'First Term', 'Second Term', 'Third Term'}
    assert 'Number Bases (Binary)' in data['curriculum']['JSS1']['Second Term']
    assert 'Bearings & Distances' in data['curriculum']['JSS2']['Third Term']
    assert 'Simultaneous Equations' in data['curriculum']['JSS3']['Second Term']
    assert 'Trigonometry' in data['topics_by_class']['JSS3']


def test_practice_topics_are_class_aware():
    assert 'Fractions' in practice.CLASS_TOPICS['JSS1']
    assert 'Directed Numbers' not in practice.CLASS_TOPICS['JSS1']
    assert 'Directed Numbers' in practice.CLASS_TOPICS['JSS2']
    assert 'Simultaneous Equations' in practice.CLASS_TOPICS['JSS3']
    session = client.post('/api/classroom/session', json={
        'learner_key': 'd' * 48, 'nickname': 'Ada', 'class_level': 'JSS1',
    }).json()
    accepted = client.post('/api/classroom/practice/start', json={
        'session_token': session['session_token'], 'class_level': 'JSS1',
        'topic': 'Fractions', 'difficulty': 'Easy', 'question_count': 5,
    })
    assert accepted.status_code == 200
    assert accepted.json()['class_level'] == 'JSS1'
    rejected = client.post('/api/classroom/practice/start', json={
        'session_token': session['session_token'], 'class_level': 'JSS1',
        'topic': 'Directed Numbers', 'difficulty': 'Easy', 'question_count': 5,
    })
    assert rejected.status_code == 422


def test_every_topic_and_level_can_build_twenty_unique_questions():
    for topic in {item for topics in practice.CLASS_TOPICS.values() for item in topics}:
        for difficulty in ('Easy', 'Medium', 'Challenge'):
            questions = practice._build_question_queue(topic, difficulty, 20)
            assert len(questions) == 20, (topic, difficulty)
            assert len({item[0] for item in questions}) == 20, (topic, difficulty)
            assert all(item[1] and item[2] and 'Step 1:' in item[3] for item in questions)


def test_twenty_question_session_completes_without_repeating_or_rate_limiting():
    session = client.post('/api/classroom/session').json()
    started = client.post('/api/classroom/practice/start', json={
        'session_token': session['session_token'], 'topic': 'Whole Numbers',
        'difficulty': 'Easy', 'question_count': 20,
    })
    assert started.status_code == 200
    prompts = [started.json()['question']]
    result = None
    for index in range(20):
        marked = client.post('/api/classroom/practice/answer', json={
            'session_token': session['session_token'], 'answer': 'not the answer',
        })
        assert marked.status_code == 200
        result = marked.json()
        if index < 19:
            following = client.post('/api/classroom/practice/next', json={
                'session_token': session['session_token'],
            })
            assert following.status_code == 200
            prompts.append(following.json()['question'])

    assert len(set(prompts)) == 20
    assert result['completed'] is True
    assert result['summary']['attempted'] == 20


def test_practice_mode_marks_answers_and_tracks_score():
    session = client.post('/api/classroom/session').json()
    fixed = ("What is 2 + 3?", "Count on from 2.", "5", "2 + 3 = 5.")
    with patch.object(practice, '_build_question_queue', return_value=[fixed] * 5):
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
    with patch.object(practice, '_build_question_queue', return_value=[fixed] * 5):
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
    with patch.object(practice, '_build_question_queue', return_value=[fixed] * 5):
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
    assert "current Maths question is in English, Yorùbá, Igbo, or Hausa" in automatic
    assert "Reply entirely in the language used" in automatic
    assert "write the final-answer value as a number word" in automatic
    assert "may ask the Maths question in Yorùbá or English" in selected
    assert "reply entirely in clear, natural Yorùbá" in selected
    assert "natural punctuation" in selected
    assert "clear pauses when the answer is read aloud" in selected
    assert "simple, modern conversational Yorùbá" in selected
    assert "Avoid deep or literary Yorùbá" in selected
    assert "Never say the numbers in English" in selected


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
    assert tutor.call_args.args[3] == 'JSS2'


def test_selected_class_reaches_the_tutor():
    session = client.post('/api/classroom/session', json={
        'learner_key': 'e' * 48, 'nickname': 'Zainab', 'class_level': 'JSS3',
    }).json()
    with patch.object(classroom_api, 'get_tutor_reply', return_value=('Let us solve it.', 0.1)) as tutor:
        response = client.post('/api/classroom/chat', json={
            'message': 'Teach me simultaneous equations',
            'session_token': session['session_token'], 'language': 'English',
        })
    assert response.status_code == 200
    assert tutor.call_args.args[3] == 'JSS3'


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
