"""Controlled tests for the V2.5 browser classroom API; no live services used."""
import base64
import inspect
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from v25_app import app
import classroom_api
import practice
import practice_progress
import diagnostic_progress
import tutor
from practice_generator import generate_question
from tutor import GEMINI_STREAMING_TTS_MODEL, GEMINI_TTS_MODEL, TTS_VOICES, _language_instruction, _pcm_to_wav, _prepare_spoken_transcript, _speech_chunks, _spoken_excerpt, get_tutor_reply

client = TestClient(app)
PROJECT_ROOT = Path(__file__).parent


def test_linear_inequality_and_graph_generators_stay_in_their_topics():
    for level in ('Easy', 'Medium', 'Challenge'):
        inequality = generate_question('Linear Inequalities', level)[0]
        graph = generate_question('Linear Graphs', level)[0]
        assert any(symbol in inequality for symbol in ('<', '>', '≥', '≤'))
        assert 'y =' in graph or 'gradient' in graph.lower()


def test_mobile_classroom_keeps_teacher_compact_and_touch_targets_accessible():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    css = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert '20260910-backgroundfix1' in html
    assert 'id="learnerNickname"' in html
    assert 'id="learnerClass"' in html
    assert "learnerNickname.value=''" in script
    assert "localStorage.setItem('roboTeacherProfiles'" in script
    assert 'id="showTeacherLogin"' in html
    assert 'id="teacherAccessKey" type="password"' in html
    assert 'id="changeLearner"' in html
    assert 'id="teacherClass"' in html
    assert 'id="downloadTeacherReport"' in html
    assert 'id="qaChecklist"' in html
    assert 'id="downloadQaReport"' in html
    assert 'const qaChecks=' in script
    assert "localStorage.setItem('roboTeacherQaChecklist'" in script
    assert 'const resultCopy=' in script
    assert 'labels.yourAnswer' in script
    assert '20260910-backgroundfix1' in html
    assert 'downloadTeacherDashboardReport' in script
    assert 'id="practiceClass"' in html
    assert 'id="startDiagnostic"' in html
    assert "diagnosticRequest('start'" in script
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
    assert '.founder-avatar{height:auto!important;aspect-ratio:1023/1537!important' in css
    assert 'min-height:44px' in css
    assert 'grid-template-columns:290px minmax(0,1fr)' in css
    assert '.classroom-screen,.classroom-screen.teacher-min{grid-template-columns:minmax(0,1fr);gap:14px}' in css
    assert '.teacher-panel{order:2;display:grid;grid-template-columns:150px minmax(0,1fr)' in css
    assert '.learning-area{order:1}' in css
    assert '.whiteboard-area canvas{aspect-ratio:2.5/1}' in css
    assert 'grid-template-columns:repeat(4,minmax(0,1fr))' in css
    assert 'overflow:visible' in css


def test_founder_portrait_is_not_cropped_on_mobile():
    css = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    assert 'object-fit:contain!important;object-position:center top!important' in css
    assert '@media(max-width:600px){.founder-panel{width:min(100%,250px)}' in css


def test_ui_refinement_exposes_clear_modes_and_activity_status():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    css = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert 'id="learningStatus"' in html
    assert 'id="chatButton"' in html
    assert 'aria-current="page"' in html
    assert 'function setActiveMode(button)' in script
    assert "setLearningStatus('Checking your answer','thinking')" in script
    assert 'Switching question to ${selectedLanguage}…' in script
    assert 'language.disabled=false' in script
    assert '.class-tools button.active' in css
    assert '.composer{position:sticky;bottom:92px' in css
    assert 'linear-gradient(135deg,#eaf7ff' in css
    assert 'void speakText(data.reply,true)' in script
    assert 'await startAudioKeepAlive();\n    await ensureSession();' in script
    assert 'data-voice-gender="female"' in html
    assert 'prepareSpeechText(text)' in script
    assert "fetch('/api/classroom/speech'" in script
    assert "voice_gender:teacherPanel.dataset.voiceGender" in script
    assert 'speechSynthesis' not in script
    assert 'teacherSpeechController.abort()' in script
    assert 'teacherAudioContext.suspend()' in script
    assert 'teacherAudioContext.resume()' in script
    assert "teacherSpeechPaused){await resumeTeacherAudio()" in script
    assert 'async function playPcmStream(response,requestId)' in script
    assert "const reader=response.body.getReader()" in script
    assert "teacherPanel.classList.add('paused')" in script
    assert "teacherPanel.classList.remove('paused')" in script
    assert '.teacher-panel.speaking .read-answer,.teacher-panel.paused .read-answer{position:fixed' in css
    assert '.read-answer span{display:none}' not in css
    assert 'teacherSpeechPaused=true;\n  teacherPanel.classList.remove' in script
    assert 'await startAudioKeepAlive();\n    await ensureSession();' in script
    assert 'function stopTeacherAudio(preserveAudioUnlock=false)' in script
    assert "showCanvasAnswer(data.reply,'Whiteboard solution ready',true)" in script
    assert "showCanvasAnswer(data.reply,'Voice question explained',true)" in script
    assert 'async function startAudioKeepAlive()' in script
    assert 'if(teacherAudioContext.state!==\'running\')' in script
    assert "teacherAudioContext.state==='closed'" in script
    assert 'teacherAudioContext.close()' not in script
    assert "'Accept':'audio/L16'" in script
    assert 'const dashboardCopy=' in script
    assert 'function learnerRecommendation(data)' in script
    assert 'function teacherAction(data)' in script
    assert "renderTeacherDashboard(currentTeacherDashboard)" in script
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
    assert tts.call_args.args[1:] == ('English', 'female', 'normal')


def test_empty_stream_uses_stable_gemini_tts_fallback():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'stream_tutor_speech', return_value=iter(())), \
         patch.object(classroom_api, 'stream_stable_tutor_speech', return_value=iter([b'fallback-', b'pcm'])) as fallback:
        response = client.post('/api/classroom/speech', json={
            'text': 'The answer is six.',
            'session_token': session['session_token'],
            'language': 'English',
            'voice_gender': 'female',
        })
    assert response.status_code == 200
    assert response.content == b'fallback-pcm'
    fallback.assert_called_once_with('The answer is six.', 'English', 'female', 'normal')


def test_voice_fallback_is_chunked_for_faster_first_audio():
    source = inspect.getsource(tutor.stream_stable_tutor_speech)
    assert "_speech_chunks(spoken_text, max_chars=220)" in source
    primary_source = inspect.getsource(tutor.stream_tutor_speech)
    assert "retry_prompt" not in primary_source


def test_pause_is_enabled_only_after_real_audio_arrives():
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert "teacherVoiceStatus.textContent='Preparing teacher voice…'" in script
    assert "readAnswerButton.disabled=true" in script
    assert "if(!receivedAudio){" in script
    assert "readAnswerButton.disabled=false;\n      setTeacherSpeaking(true)" in script


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
    assert dashboard['weekly_summary']['strongest_topic'] == 'Factorisation & Quadratic Expressions'
    assert dashboard['weekly_summary']['focus_topic'] == 'Factorisation & Quadratic Expressions'
    assert 'easier level' in dashboard['weekly_summary']['next_action']


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


def test_auto_difficulty_uses_topic_history_without_skipping_a_level():
    practice_progress._reset_for_tests()
    now = __import__('datetime').datetime.now(__import__('datetime').UTC)
    practice_progress._memory_records.extend([
        {'learner_id': 'WEB-auto', 'class_level': 'JSS1', 'session_id': 'easy-1', 'topic': 'Fractions', 'difficulty': 'Easy', 'score': 5, 'attempted': 5, 'percentage': 100, 'timestamp': (now-__import__('datetime').timedelta(days=2)).isoformat()},
        {'learner_id': 'WEB-auto', 'class_level': 'JSS1', 'session_id': 'easy-2', 'topic': 'Fractions', 'difficulty': 'Easy', 'score': 5, 'attempted': 5, 'percentage': 100, 'timestamp': (now-__import__('datetime').timedelta(days=1)).isoformat()},
        {'learner_id': 'WEB-auto', 'class_level': 'JSS1', 'session_id': 'medium-1', 'topic': 'Fractions', 'difficulty': 'Medium', 'score': 5, 'attempted': 5, 'percentage': 100, 'timestamp': now.isoformat()},
    ])
    assert practice_progress.recommend_difficulty_for_topic('WEB-auto', 'JSS1', 'Fractions') == 'Medium'


def test_practice_auto_difficulty_is_resolved_before_session_starts():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'recommend_difficulty_for_topic', return_value='Challenge') as recommend, patch.object(classroom_api, 'start_practice', return_value={'difficulty': 'Challenge'}) as start:
        response = client.post('/api/classroom/practice/start', json={
            'session_token': session['session_token'], 'topic': 'Fractions',
            'difficulty': 'Auto', 'question_count': 5, 'class_level': 'JSS1', 'language': 'English',
        })
    assert response.status_code == 200
    assert response.json()['difficulty_was_automatic'] is True
    recommend.assert_called_once_with(session['learner_id'], 'JSS1', 'Fractions')
    assert start.call_args.args[2] == 'Challenge'


def test_diagnostic_placement_is_separate_and_privacy_safe():
    diagnostic_progress._memory.clear();practice_progress._reset_for_tests()
    diagnostic_progress._memory.append({'timestamp':'2026-09-06T10:00:00+00:00','session_id':'diagnostic-1','learner_id':'WEB-diagnostic','class_level':'JSS1','term':'First Term','score':6,'attempted':10,'percentage':60,'recommended_topic':'Fractions','recommended_difficulty':'Medium','topic_results':[]})
    dashboard=practice_progress.build_dashboard('WEB-diagnostic','JSS1')
    assert dashboard['sessions']==0
    assert dashboard['recommended_topic']=='Fractions'
    assert dashboard['recommended_difficulty']=='Medium'
    assert dashboard['recommendation_reason']=='diagnostic'
    assert 'learner_id' not in dashboard['latest_diagnostic']


def test_teacher_dashboard_returns_aggregates_without_identities():
    practice_progress._reset_for_tests()
    diagnostic_progress._memory.clear()
    current_timestamp = datetime.now(timezone.utc).isoformat()
    diagnostic_progress._memory.append({'timestamp':current_timestamp,'session_id':'class-diagnostic','learner_id':'WEB-private','class_level':'JSS2','term':'First Term','score':6,'attempted':10,'percentage':60,'recommended_topic':'Standard Form','recommended_difficulty':'Medium','topic_results':[]})
    practice_progress._memory_records.append({
        'learner_id': 'WEB-private', 'class_level': 'JSS2', 'session_id': 'aggregate-1',
        'topic': 'Simple Equations', 'difficulty': 'Easy', 'score': 4, 'attempted': 5,
            'percentage': 80, 'timestamp': current_timestamp,
    })
    dashboard = practice_progress.build_teacher_dashboard('JSS2')
    assert dashboard['learners'] == 1
    assert dashboard['average_percentage'] == 80
    assert dashboard['strongest_topic'] == 'Simple Equations'
    assert dashboard['weakest_topic'] == 'Simple Equations'
    assert dashboard['recommendation']
    assert len(dashboard['weekly_trend']) == 6
    assert dashboard['weekly_summary']['sessions'] == 1
    assert dashboard['weekly_summary']['strongest_topic'] == 'Simple Equations'
    assert dashboard['weekly_summary']['weakest_topic'] == 'Simple Equations'
    assert dashboard['weekly_summary']['action']
    assert 'learner_id' not in dashboard
    assert 'recent_sessions' not in dashboard
    assert dashboard['diagnostic_summary']['completed'] == 1
    assert dashboard['diagnostic_summary']['common_focus_topic'] == 'Standard Form'
    assert 'learner_id' not in dashboard['diagnostic_summary']


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


def test_practice_mode_uses_selected_language_without_changing_marking():
    session = client.post('/api/classroom/session').json()
    english = ("What is 2 + 3?", "Add the numbers.", "5", "Step 1: Add 2 and 3.\nTherefore, the answer is 5.")
    yoruba = ("Kí ni 2 + 3?", "Da àwọn nọ́mbà náà pọ̀.", "5", "Ìgbésẹ̀ 1: Da 2 àti 3 pọ̀.\nNítorí náà, ìdáhùn jẹ́ 5.")
    with patch.object(practice, '_build_question_queue', return_value=[english] * 5), patch.object(practice, 'translate_question_batch', return_value=[yoruba] * 5) as translated:
        started = client.post('/api/classroom/practice/start', json={
            'session_token': session['session_token'], 'topic': 'Standard Form',
            'class_level': 'JSS2', 'difficulty': 'Easy', 'language': 'Yoruba',
        })
        marked = client.post('/api/classroom/practice/answer', json={
            'session_token': session['session_token'], 'answer': '5',
        })
    assert started.json()['question'] == yoruba[0]
    assert translated.call_args.args[1] == 'Yoruba'
    assert marked.json()['correct'] is True
    assert marked.json()['correct_answer_label'] == 'Ìdáhùn tó tọ́'
    assert marked.json()['message'] in practice.PRACTICE_TEXT['Yoruba']['correct']


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
    assert "Reply in at least 90 percent of the language used" in automatic
    assert "write the final-answer value as a number word" in automatic
    assert "may ask the Maths question in Yorùbá or English" in selected
    assert "reply in at least 90 percent Yorùbá" in selected
    assert "natural punctuation" in selected
    assert "clear pauses when the answer is read aloud" in selected
    assert "simple, modern conversational Yorùbá" in selected
    assert "Avoid deep, literary, ceremonial or old-fashioned Yorùbá" in selected
    assert "Never say explanatory numbers in English" in selected


def test_igbo_and_hausa_language_instructions_cover_text_and_voice():
    for language in ("Igbo", "Hausa"):
        instruction = _language_instruction(language)
        assert "at least 90 percent" in instruction
        assert "Never write a complete explanatory sentence in English" in instruction
        assert "deep" in instruction
        assert "silently check every sentence" in instruction
        assert f"ask the Maths question in {language} or English" in instruction
        assert f"reply in at least 90 percent {language}" in instruction


def test_native_language_prompts_limit_english_to_unavoidable_maths_terms():
    for language in ("Yoruba", "Igbo", "Hausa"):
        instruction = _language_instruction(language, "JSS1")
        assert "Translate the teaching itself" in instruction
        assert "English is permitted only for a standard Maths term" in instruction
        assert "formula letters, units and proper names" in instruction
    assert "did not grow up in their ancestral town" in _language_instruction("Yoruba")
    assert "did not grow up in an Igbo-speaking hometown" in _language_instruction("Igbo")
    assert "Hausa is not the main language spoken in their home" in _language_instruction("Hausa")


def test_active_voice_language_change_translates_and_restarts_stream():
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert "const wasReading=teacherPanel.classList.contains('speaking')||teacherSpeechPaused" in script
    assert "fetch('/api/classroom/translate'" in script
    assert "renderLesson(canvasAnswer,data.translation)" in script
    assert "void speakText(data.translation,true)" in script


def test_language_change_always_translates_visible_answer_and_only_resumes_active_voice():
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert "if(answerToTranslate){" in script
    assert "if(wasReading)void speakText(data.translation,true)" in script
    assert "!receivedAudio)throw new Error('empty voice stream')" in script


def test_translate_endpoint_preserves_selected_language_and_class():
    session = client.post('/api/classroom/session', json={
        'learner_key': 'f' * 48, 'nickname': 'Ada', 'class_level': 'JSS3',
    }).json()
    with patch.object(classroom_api, 'translate_tutor_text', return_value='Ka anyị gaa n’ihu.') as translator:
        response = client.post('/api/classroom/translate', json={
            'session_token': session['session_token'],
            'text': 'Let us continue.', 'language': 'Igbo',
        })
    assert response.status_code == 200
    assert response.json() == {'translation': 'Ka anyị gaa n’ihu.', 'language': 'Igbo'}
    assert translator.call_args.args == ('Let us continue.', 'Igbo', 'JSS3')


def test_translation_function_explicitly_targets_english():
    import tutor
    fake_response = type('Response', (), {'text': 'The answer is six.', 'candidates': []})()
    fake_models = type('Models', (), {'generate_content': lambda self, **kwargs: fake_response})()
    fake_client = type('Client', (), {'models': fake_models})()
    with patch.object(tutor, '_get_client', return_value=fake_client):
        assert tutor.translate_tutor_text('Ìdáhùn ni mẹ́fà.', 'English') == 'The answer is six.'


def test_practice_translation_prompt_requires_mostly_native_language():
    from practice_translation import LANGUAGE_STYLE
    assert "modern conversational Yorùbá" in LANGUAGE_STYLE["Yoruba"]
    assert "modern everyday Igbo" in LANGUAGE_STYLE["Igbo"]
    assert "modern everyday Hausa" in LANGUAGE_STYLE["Hausa"]


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


def test_active_practice_switches_question_feedback_and_remaining_language():
    session = client.post('/api/classroom/session').json()
    questions = [
        (f'English question {number}', f'English hint {number}', str(number), f'English explanation {number}')
        for number in range(1, 6)
    ]

    def translated(items, language):
        if language == 'English':
            return items
        return [
            (f'{language} question {index}', f'{language} hint {index}', answer, f'{language} explanation {index}')
            for index, (_question, _hint, answer, _explanation) in enumerate(items, 1)
        ]

    with patch.object(practice, '_build_question_queue', return_value=questions), patch.object(practice, 'translate_question_batch', side_effect=translated) as translate:
        started = client.post('/api/classroom/practice/start', json={
            'session_token': session['session_token'], 'topic': 'Whole Numbers',
            'difficulty': 'Easy', 'question_count': 5, 'class_level': 'JSS2', 'language': 'English',
        })
        assert started.json()['question'] == 'English question 1'

        client.post('/api/classroom/practice/answer', json={'session_token': session['session_token'], 'answer': '0'})
        switched = client.post('/api/classroom/practice/language', json={
            'session_token': session['session_token'], 'language': 'Yoruba',
        })
        body = switched.json()
        assert body['question'] == 'Yoruba question 1'
        assert body['feedback']['explanation'] == 'Yoruba explanation 1'
        assert body['feedback']['expected_answer'] == '1'

        following = client.post('/api/classroom/practice/next', json={'session_token': session['session_token']})
        assert following.json()['question'] == 'Yoruba question 2'

        switched_back = client.post('/api/classroom/practice/language', json={
            'session_token': session['session_token'], 'language': 'English',
        })
        assert switched_back.json()['question'] == 'English question 2'
        assert translate.call_count == 2


def test_explain_simpler_replaces_duplicate_voice_control():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert 'id="simplifyButton"' in html
    assert '>Explain Simpler</button>' in html
    assert 'id="navMicButton"' not in html
    assert "fetch('/api/classroom/simplify'" in script
    assert "showCanvasAnswer(data.explanation,'Simpler explanation',true)" in script
    assert 'void speakText(data.explanation,true)' in script


def test_simplify_endpoint_preserves_language_and_class():
    session = client.post('/api/classroom/session', json={
        'learner_key': 'e' * 48, 'nickname': 'Bola', 'class_level': 'JSS1',
    }).json()
    with patch.object(classroom_api, 'simplify_tutor_text', return_value='Jẹ́ ká lo àpẹẹrẹ tó rọrùn.') as simplifier:
        response = client.post('/api/classroom/simplify', json={
            'session_token': session['session_token'],
            'text': 'Existing worked answer', 'language': 'Yoruba',
        })
    assert response.status_code == 200
    assert response.json() == {'explanation': 'Jẹ́ ká lo àpẹẹrẹ tó rọrùn.', 'language': 'Yoruba'}
    assert simplifier.call_args.args == ('Existing worked answer', 'Yoruba', 'JSS1')


def test_simplify_prompt_preserves_maths_and_adds_one_example():
    fake_response = type('Response', (), {'text': 'Simpler answer.', 'candidates': []})()
    generate_content = Mock(return_value=fake_response)
    fake_client = type('Client', (), {'models': type('Models', (), {'generate_content': generate_content})()})()
    with patch.object(tutor, '_get_client', return_value=fake_client):
        assert tutor.simplify_tutor_text('2 + 2 = 4', 'English', 'JSS2') == 'Simpler answer.'
    prompt = generate_content.call_args.kwargs['contents']
    assert 'one familiar everyday example' in prompt
    assert 'Preserve every equation, value, operation, unit and final answer exactly' in prompt


def test_check_my_understanding_ui_is_tied_to_current_lesson():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    assert 'id="understandingButton"' in html
    assert 'id="understandingArea"' in html
    assert "fetch('/api/classroom/understanding/start'" in script
    assert "fetch('/api/classroom/understanding/answer'" in script
    assert "choice_index:Number(selected.value)" in script


def test_understanding_check_is_private_to_the_learner_and_marks_locally():
    first = client.post('/api/classroom/session').json()
    second = client.post('/api/classroom/session').json()
    generated = {'question': 'What is 2 + 2?', 'choices': ['3', '4', '5'], 'correct_index': 1, 'feedback': 'Add the two values to get 4.'}
    with patch.object(classroom_api, 'generate_understanding_check', return_value=generated):
        started = client.post('/api/classroom/understanding/start', json={'session_token': first['session_token'], 'text': 'Two plus two equals four.', 'language': 'English'})
    assert started.status_code == 200
    body = started.json();assert 'correct_index' not in body
    marked = client.post('/api/classroom/understanding/answer', json={'session_token': first['session_token'], 'check_id': body['check_id'], 'choice_index': 1})
    assert marked.json() == {'correct': True, 'correct_index': 1, 'feedback': generated['feedback']}
    blocked = client.post('/api/classroom/understanding/answer', json={'session_token': second['session_token'], 'check_id': body['check_id'], 'choice_index': 1})
    assert blocked.status_code == 404


def test_understanding_generator_requires_three_valid_choices():
    payload = {'question': 'What comes next?', 'choices': ['2', '3', '4'], 'correct_index': 2, 'feedback': 'Count forward once.'}
    fake_response = type('Response', (), {'text': __import__('json').dumps(payload), 'candidates': []})()
    generate_content = Mock(return_value=fake_response)
    fake_client = type('Client', (), {'models': type('Models', (), {'generate_content': generate_content})()})()
    with patch.object(tutor, '_get_client', return_value=fake_client):
        assert tutor.generate_understanding_check('The sequence is 2, 3, 4.', 'English')['correct_index'] == 2
    prompt = generate_content.call_args.kwargs['contents']
    assert 'exactly one short multiple-choice question' in prompt
    assert 'Do not introduce a topic not taught' in prompt


def test_visual_teaching_mode_minimizes_avatar_and_renders_safe_data():
    html=(PROJECT_ROOT/'classroom'/'index.html').read_text();script=(PROJECT_ROOT/'classroom'/'app.js').read_text()
    assert 'id="visualButton"' in html and 'id="visualArea"' in html
    assert "fetch('/api/classroom/visual'" in script
    assert "teacherPanel.classList.add('minimized')" in script
    assert 'visualTitle.textContent=data.title' in script
    assert 'innerHTML=data' not in script


def test_visual_endpoint_uses_selected_language_and_class():
    session=client.post('/api/classroom/session',json={'learner_key':'d'*48,'nickname':'Tola','class_level':'JSS3'}).json()
    visual={'title':'Number line','kind':'number_line','items':[{'label':'Start','value':2},{'label':'End','value':5}],'caption':'Move three places.'}
    with patch.object(classroom_api,'generate_visual_aid',return_value=visual) as generator:
        response=client.post('/api/classroom/visual',json={'session_token':session['session_token'],'text':'Move from 2 to 5.','language':'Yoruba'})
    assert response.status_code==200 and response.json()==visual
    assert generator.call_args.args==('Move from 2 to 5.','Yoruba','JSS3')


def test_topic_specific_visual_renderers_are_safe_and_mobile_ready():
    script=(PROJECT_ROOT/'classroom'/'app.js').read_text();css=(PROJECT_ROOT/'classroom'/'styles.css').read_text()
    for kind in ('square_grid','fraction','balance','coordinate'):
        assert f"data.kind==='{kind}'" in script
    assert "cell.setAttribute('aria-hidden','true')" in script
    assert '.square-grid' in css and '.fraction-model' in css and '.balance-model' in css and '.coordinate-model' in css


def test_visual_generator_accepts_a_true_square_grid():
    payload={'title':'Square root of 49','kind':'square_grid','items':[{'label':'49 cells','value':49},{'label':'7 by 7','value':7}],'caption':'Seven rows of seven.'}
    fake_response=type('Response',(),{'text':__import__('json').dumps(payload),'candidates':[]})();generate_content=Mock(return_value=fake_response);fake_client=type('Client',(),{'models':type('Models',(),{'generate_content':generate_content})()})()
    with patch.object(tutor,'_get_client',return_value=fake_client): result=tutor.generate_visual_aid('The square root of 49 is 7.','English','JSS2')
    assert result['kind']=='square_grid' and result['items'][0]['value']==49


def test_visual_generator_normalizes_common_model_variations():
    payload={'title':'Equation balance','kind':'balance_scale','items':[{'name':'Left','value':'x + 4'},{'name':'Right','value':'9'}],'caption':'Keep both sides equal.'}
    fake_response=type('Response',(),{'text':__import__('json').dumps(payload),'candidates':[]})();generate_content=Mock(return_value=fake_response);fake_client=type('Client',(),{'models':type('Models',(),{'generate_content':generate_content})()})()
    with patch.object(tutor,'_get_client',return_value=fake_client): result=tutor.generate_visual_aid('Solve x + 4 = 9.','English','JSS2')
    assert result['kind']=='balance' and result['items'][0]['value']=='x + 4' and result['items'][1]['value']==9.0


def test_coordinate_renderer_accepts_parenthesized_points():
    script=(PROJECT_ROOT/'classroom'/'app.js').read_text()
    assert "\\(?\\s*(-?\\d+" in script and "\\)?\\s*$/" in script


def test_coordinate_visual_is_deterministic_and_uses_no_model_request():
    with patch.object(tutor,'_get_client') as client_factory:
        result=tutor.generate_visual_aid('Plot the points (1,2), (2,4), and (3,6).','English','JSS2')
    assert result['kind']=='coordinate'
    assert [item['label'] for item in result['items']]==['1,2','2,4','3,6']
    client_factory.assert_not_called()


def test_watch_example_uses_only_allowlisted_phet_or_local_replay():
    fraction=tutor.select_lesson_media('The numerator and denominator form a fraction.','English')
    assert fraction['kind']=='simulation' and fraction['url'].startswith('https://phet.colorado.edu/sims/html/')
    replay=tutor.select_lesson_media('The square root of 49 is 7.','English')
    assert replay['kind']=='replay' and replay['source']=='Robo-Teacher' and replay['steps']


def test_watch_example_ui_minimizes_avatar_and_stops_embedded_media():
    html=(PROJECT_ROOT/'classroom'/'index.html').read_text();script=(PROJECT_ROOT/'classroom'/'app.js').read_text()
    assert 'id="mediaButton"' in html and 'id="mediaFrame"' in html
    assert "fetch('/api/classroom/media'" in script
    assert "mediaFrame.removeAttribute('src')" in script
    assert "teacherPanel.classList.add('minimized')" in script


def test_mobile_simulation_always_exposes_an_escape_control():
    html=(PROJECT_ROOT/'classroom'/'index.html').read_text();css=(PROJECT_ROOT/'classroom'/'styles.css').read_text()
    assert 'class="exit-media"' in html
    assert '← Exit simulation' in html
    assert 'allowfullscreen' not in html
    assert '.media-area>.exit-media{position:fixed' in css
    assert 'height:55vh' in css and 'overscroll-behavior:contain' in css


def test_mobile_toolbar_is_one_scrollable_row_and_replay_keeps_paragraphs():
    html=(PROJECT_ROOT/'classroom'/'index.html').read_text();script=(PROJECT_ROOT/'classroom'/'app.js').read_text();css=(PROJECT_ROOT/'classroom'/'styles.css').read_text()
    assert '>Watch or Explore</button>' in html
    assert "map(item=>item.innerText.trim()).filter(Boolean).join('\\n')" in script
    assert 'flex-wrap:nowrap!important' in css and 'overflow-x:auto!important' in css
    assert "data.kind==='simulation'?'← Exit simulation':'← Exit example'" in script


def test_switching_modes_unloads_media_before_showing_new_content():
    script=(PROJECT_ROOT/'classroom'/'app.js').read_text()
    assert 'function dismissLessonOverlays(){stopLessonMedia()' in script
    assert "mediaFrame.removeAttribute('src')" in script
    assert 'dismissLessonOverlays();restoreTeacherPanel();' in script
    assert "dismissLessonOverlays();renderVisualAid(data)" in script
    assert "stopTeacherAudio(preserveAudioUnlock);\n  dismissLessonOverlays();restoreTeacherPanel();" in script


def test_teacher_portrait_animates_only_during_active_speech():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    styles = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    assert 'ai-teacher-face.jpg' in html
    assert 'ai-teacher-face-speaking.jpg' in html
    assert 'avatar-speaking-frame' in html
    assert '.teacher-panel.paused .avatar-speaking-frame' in styles
    assert '.teacher-panel.speaking .teacher-avatar:not(.avatar-head-motion){animation:none;transform:none}' in styles
    assert '@media(prefers-reduced-motion:reduce)' in styles


def test_audio_driven_avatar_engine_supports_teacher_and_founder():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    styles = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    assert 'id="founderPanel"' in html
    assert 'id="hearFounder"' in html
    assert 'herbert-stephen-founder-speaking.jpg' in html
    assert 'function startAvatarMotion(rig)' in script
    assert 'Math.round(Math.max(0,Math.min(1,avatarEnergy*pulse))*120)/120' in script
    assert "voice_gender:'male'" in script
    assert '.avatar-speaking-frame{position:absolute;inset:0;opacity:var(--mouth-open)' in styles


def test_mobile_pause_control_stays_outside_avatar_face():
    styles = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    assert '.teacher-panel.speaking .read-answer,.teacher-panel.paused .read-answer{position:static' in styles


def test_voice_status_is_in_toolbar_and_portrait_stays_fixed():
    html = (PROJECT_ROOT / 'classroom' / 'index.html').read_text()
    script = (PROJECT_ROOT / 'classroom' / 'app.js').read_text()
    styles = (PROJECT_ROOT / 'classroom' / 'styles.css').read_text()
    actions = html.split('<div class="teacher-actions">', 1)[1].split('</div>', 1)[0]
    portrait = html.split('<div class="teacher-portrait">', 1)[1].split('</div>', 2)[0]
    assert 'id="teacherVoiceStatus"' in actions
    assert 'id="teacherVoiceStatus"' not in portrait
    assert '.teacher-actions .teacher-voice-status{position:static' in styles
    assert '.avatar-stage{position:relative;transform:none}' in styles


def test_head_only_rig_and_voice_question_canvas_avatar():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'founder-head-motion' in html
    assert 'teacher-head-motion' in html
    assert 'id="canvasVoiceAvatar"' in html
    assert 'void speakText(data.reply,true,true)' in script
    assert 'displayCanvasAvatar=true' in script
    assert "canvasWork.classList.toggle('voice-avatar-visible',visible)" in script
    assert '.canvas-work.voice-avatar-visible{padding-right:140px' in styles
    assert '.avatar-head-motion{' in styles


def test_interactive_lesson_director_supports_steps_and_interruption_recovery():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    for control in ('lessonDirector', 'previousLessonStep', 'nextLessonStep', 'replayLessonStep', 'returnToLesson', 'endLesson'):
        assert f'id="{control}"' in html
    assert 'function splitLessonSteps(text)' in script
    assert 'function renderCurrentLessonStep()' in script
    assert 'lessonHistory.push(interruptedLesson)' in script
    assert "void speakText(currentLesson.steps[currentLesson.index])" in script
    assert '.lesson-director{' in styles


def test_lesson_interruption_engine_handles_text_and_voice_detours():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="askLessonQuestion"' in html
    assert 'id="lessonPauseNotice"' in html
    assert "function pauseLessonForQuestion(source='text')" in script
    assert "if(currentLesson)pauseLessonForQuestion('voice')" in script
    assert 'The learner paused this lesson step:' in script
    assert '.lesson-pause-notice{' in styles


def test_smart_teaching_stage_coordinates_step_media_and_restores_bookmark():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    for control in ('teachingStageMode', 'showStepVisual', 'watchStepExample', 'checkStepUnderstanding'):
        assert f'id="{control}"' in html
    assert 'function enterTeachingStage(mode)' in script
    assert 'function restoreTeachingStage()' in script
    assert "enterTeachingStage('visual')" in script
    assert "enterTeachingStage('example')" in script
    assert "enterTeachingStage('check')" in script
    assert '.lesson-stage-actions{' in styles
    assert "rig.style.setProperty('--head-x'" not in script.split('function startAvatarMotion(rig)', 1)[1].split('async function startAudioKeepAlive', 1)[0]


def test_automatic_lesson_choreography_recommends_and_opens_each_mode_once():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="autoTeachToggle"' in html
    assert 'id="lessonChoreographyHint"' in html
    assert 'function chooseTeachingMode(step,index,total)' in script
    assert 'function scheduleLessonChoreography()' in script
    assert 'lessonChoreography.visited.has(key)' in script
    assert "choice.mode==='visual'" in script
    assert '.auto-teach-toggle[aria-pressed="true"]' in styles
    assert '.lesson-stage-actions button.recommended' in styles


def test_visual_failure_uses_quota_free_fallback_and_client_retries_transient_errors():
    session = client.post('/api/classroom/session').json()
    with patch.object(classroom_api, 'generate_visual_aid', side_effect=RuntimeError('quota')):
        response = client.post('/api/classroom/visual', json={'session_token': session['session_token'], 'text': 'Step 1: Add two. Step 2: Check the answer.', 'language': 'English'})
    assert response.status_code == 200
    assert response.json()['kind'] == 'steps'
    assert len(response.json()['items']) >= 2
    script = Path('classroom/app.js').read_text()
    assert 'for(let attempt=1;attempt<=3;attempt++)' in script
    assert "[429,503].includes(response.status)" in script


def test_adaptive_teaching_memory_records_signals_and_changes_support_level():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="teachingMemoryStatus"' in html
    assert 'function recordLearningSignal(signal)' in script
    assert 'function adaptiveSupportLevel()' in script
    assert 'function adaptivePromptContext()' in script
    for signal in ('replays', 'simplifications', 'questions', 'correct', 'incorrect'):
        assert signal in script
    assert "localStorage.setItem(`roboTeacherMemory:${learnerMemoryId}`" in script
    assert "adaptiveSupportLevel()==='support'" in script
    assert '.teaching-memory-status[data-level="support"]' in styles


def test_hands_free_teaching_pauses_questions_and_resumes_bookmarked_step():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="handsFreeToggle"' in html
    assert 'window.SpeechRecognition||window.webkitSpeechRecognition' in script
    assert 'function handleHandsFreePhrase(rawPhrase)' in script
    assert "pauseLessonForQuestion('voice')" in script
    assert 'form.requestSubmit()' in script
    assert 'function resumeBookmarkedLessonByVoice()' in script
    assert 'const lesson=lessonHistory.pop()' in script
    assert 'void speakText(step,true,true)' in script
    assert "if(handsFree.enabled)void speakText(data.reply,true,true)" in script
    assert '.hands-free-toggle[aria-pressed="true"]' in styles


def test_mobile_answer_closes_keyboard_keeps_canvas_visible_and_wraps_voice_controls():
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'function keepTeachingCanvasVisible()' in script
    assert "if(document.activeElement===question)question.blur()" in script
    assert "teachingCanvas.scrollIntoView({block:'start',behavior:'smooth'})" in script
    assert "window.matchMedia('(min-width: 701px)').matches&&!handsFree.enabled" not in script
    assert 'flex-wrap:wrap!important' in styles
    assert '.teacher-actions .hands-free-toggle{flex:1 1 100%' in styles


def test_cross_device_controls_wrap_and_all_answers_keep_canvas_visible():
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert "if(!window.matchMedia('(max-width: 700px)').matches)return" not in script
    assert "setLearningStatus('Answer ready');keepTeachingCanvasVisible()" in script
    assert '.teacher-toolbar>strong{flex:1 1 100%}' in styles
    assert '.composer>*{min-width:0}' in styles
    assert '@media(min-width:601px) and (max-width:1100px)' in styles


def test_wake_word_mode_ignores_background_and_confirms_uncertain_commands():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="handsFreeHeard"' in html
    assert 'function executeHandsFreeIntent(phrase)' in script
    assert 'function handleHandsFreePhrase(rawPhrase,confidence=0)' in script
    assert "(?:robo|robot|robotic)\\s*(?:teacher|tutor|feature)" in script
    assert 'start with “Robo-Teacher”' in script
    assert "confidence>0&&confidence<.55" in script
    assert "handsFree.pending=intent" in script
    for command in ('explain (that )?again', 'show (me )?(a )?visual', 'stop listening'):
        assert command in script
    assert '.hands-free-heard{' in styles


def test_wake_word_and_command_can_arrive_as_separate_speech_results():
    script = Path('classroom/app.js').read_text()
    assert 'armedUntil:0' in script
    assert 'handsFree.armedUntil=now+7000' in script
    assert 'else if(now<handsFree.armedUntil)' in script
    assert 'handsFree.recognition.interimResults=true' in script
    assert 'for(let index=event.resultIndex;index<event.results.length;index++)' in script
    assert 'Wake word heard. Say the command within 7 seconds.' in script


def test_child_speech_selects_richer_alternatives_and_handles_command_sound_alikes():
    script = Path('classroom/app.js').read_text()
    assert 'handsFree.recognition.maxAlternatives=5' in script
    assert 'function chooseBestSpeechAlternative(result)' in script
    assert 'square root|square route|squared root|fraction|multiply|divide' in script
    assert 'function queueHandsFreePhrase(rawPhrase,confidence=0)' in script
    assert '},800)' in script
    assert "replace(/^(?:pulse|pals|paws|pose|pores)$/,'pause')" in script
    assert '· Interpreted: “${interpretedIntent}”' in script


def test_hands_free_pause_can_interrupt_teacher_playback_without_echo_submission():
    script = Path('classroom/app.js').read_text()
    assert 'function handsFreeBargeIn(result)' in script
    assert "teacherPanel.classList.contains('speaking')" in script
    assert 'void pauseTeacherAudio()' in script
    assert "updateHandsFreeStatus('Paused')" in script
    assert 'teacher paused so I can hear you.' in script
    assert 'if(handsFreeBargeIn(result))continue' in script


def test_hands_free_continue_resumes_audio_or_the_bookmarked_lesson_context():
    script = Path('classroom/app.js').read_text()
    assert 'function continueHandsFreeTeaching()' in script
    assert 'if(lessonHistory.length||lessonInterruption){resumeBookmarkedLessonByVoice();return}' in script
    assert 'if(teacherSpeechPaused){void resumeTeacherAudio();return}' in script
    assert "if(teacherPanel.classList.contains('speaking'))void pauseTeacherAudio()" in script
    assert 'const pausedControl=teacherSpeechPaused&&' in script
    assert 'continueHandsFreeTeaching();' in script


def test_pause_opens_a_limited_wake_free_follow_up_window():
    script = Path('classroom/app.js').read_text()
    assert 'function openHandsFreeFollowUpWindow()' in script
    assert 'handsFree.armedUntil=Date.now()+15000' in script
    assert "updateHandsFreeStatus('Ask or say Continue…')" in script
    assert 'Ask your follow-up within 15 seconds' in script
    assert script.count('openHandsFreeFollowUpWindow();') >= 2


def test_unclear_child_speech_accepts_simple_confirmation_or_correction():
    script = Path('classroom/app.js').read_text()
    assert 'const clarificationReply=Boolean(handsFree.pending)' in script
    assert 'yes|yes please|correct' in script
    assert 'no|nope|cancel|try again|listen again' in script
    assert 'handsFree.armedUntil=now+15000' in script
    assert 'Say “Yes”, “No”, “Try again”, or say the correction.' in script
    assert 'Correction heard: “${intent}”' in script


def test_hands_free_local_language_commands_work_during_teacher_playback():
    script = Path('classroom/app.js').read_text()
    assert 'function handsFreeWakePattern()' in script
    for phrase in ('olukọ', 'oluko', 'malami', 'onye\\s+nkuzi'):
        assert phrase in script
    for phrase in ('duro', 'dúró', 'kwusi', 'kwụsị', 'dakata', 'dakatar'):
        assert phrase in script
    for phrase in ('tesiwaju', 'tẹ̀síwájú', 'ga nihu', 'gaa nihu', 'ci gaba'):
        assert phrase in script
    assert "new RegExp(`^(?:(?:hey\\\\s+)?" in script


def test_hands_free_can_control_existing_pedagogical_tools():
    script = Path('classroom/app.js').read_text()
    assert 'const simplerCommand=' in script
    assert 'const understandingCommand=' in script
    assert 'const nextStepCommand=' in script
    assert 'const previousStepCommand=' in script
    assert 'void simplifyCurrentAnswer()' in script
    assert 'void startUnderstandingCheck()' in script
    assert 'moveLessonStep(1)' in script
    assert 'moveLessonStep(-1)' in script
    assert 'function replayCurrentTeachingAudio()' in script


def test_safe_replay_control_bypasses_low_confidence_question_confirmation():
    script = Path('classroom/app.js').read_text()
    assert 'function isSafeHandsFreeControl(intent)' in script
    assert 'repeat(?: that)?' in script
    assert 'confidence<.55&&!isSafeHandsFreeControl(intent)' in script
    assert "setLearningStatus('Repeating this explanation','thinking')" in script
    assert 'void speakText(text,false,true)' in script


def test_teacher_voice_speed_uses_natural_tts_pacing_and_responsive_controls():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="teacherSpeed"' in html
    assert "pace:teacherSpeechPace" in script
    assert 'function setTeacherSpeechPace(pace,replay=false)' in script
    for command in ('speak slower', 'normal speed', 'speak faster'):
        assert command in script
    assert "localStorage.setItem('roboTeacherSpeechPace'" in script
    assert '.teacher-speed{' in styles
    assert '_speech_pace_direction(pace)' in inspect.getsource(tutor.stream_tutor_speech)
    assert '_speech_pace_direction(pace)' in inspect.getsource(tutor.stream_stable_tutor_speech)


def test_teacher_volume_changes_the_live_audio_graph_and_supports_voice_commands():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="teacherVolume"' in html
    assert 'function setTeacherVolumeLevel(level,resumeAfter=false)' in script
    assert 'teacherAudioAnalyser.connect(teacherAudioGain)' in script
    assert 'teacherAudioGain.connect(context.destination)' in script
    assert 'gain.setTargetAtTime' in script
    for command in ('volume up', 'volume down', 'mute', 'unmute'):
        assert command in script
    assert "localStorage.setItem('roboTeacherVolume'" in script
    assert '.teacher-speed,.teacher-volume{' in styles


def test_hands_free_help_lists_supported_commands_without_covering_the_lesson():
    html = Path('classroom/index.html').read_text()
    script = Path('classroom/app.js').read_text()
    styles = Path('classroom/styles.css').read_text()
    assert 'id="voiceHelpToggle"' in html
    assert 'id="handsFreeHelp"' in html
    assert 'function renderHandsFreeHelp()' in script
    assert 'function showHandsFreeHelp(show=true)' in script
    for command in ('Robo olùkọ́', 'Robo onye nkuzi', 'Robo malami', 'Explain it simpler'):
        assert command in script
    assert 'const helpCommand=' in script
    assert '.hands-free-help{' in styles


def test_voice_help_restores_hidden_teacher_and_accepts_help_sound_alikes():
    script = Path('classroom/app.js').read_text()
    assert "replace(/^(?:health|held|help me)$/,'help')" in script
    assert 'if(show)restoreTeacherPanel()' in script
    assert "handsFreeHelp.scrollIntoView({block:'nearest',behavior:'smooth'})" in script
    assert 'test(normalizeSpokenIntent(command))' in script


def test_hands_free_recovers_from_browser_network_and_microphone_interruptions():
    script = Path('classroom/app.js').read_text()
    assert 'function scheduleHandsFreeRecovery' in script
    assert "updateHandsFreeStatus(`Reconnecting… ${handsFree.restartAttempts}`)" in script
    assert 'Math.min(500*2**(handsFree.restartAttempts-1),8000)' in script
    assert "window.addEventListener('online'" in script
    assert "document.addEventListener('visibilitychange'" in script
    assert "handsFree.recognition.addEventListener('start'" in script
    assert 'Date.now()-handsFree.startedAt>5000' in script
    assert "event.error==='not-allowed'&&!handsFree.hasStarted&&document.visibilityState==='visible'" in script
    assert "event.error==='aborted'&&(!handsFree.enabled||handsFree.processing)" in script
    assert "scheduleHandsFreeRecovery('answer-complete')" in script
    assert "document.visibilityState==='hidden'" in script
    assert "updateHandsFreeStatus('Paused in background…')" in script
    assert 'handsFree.hasStarted=true' in script


def test_media_endpoint_requires_a_valid_session():
    session=client.post('/api/classroom/session').json()
    response=client.post('/api/classroom/media',json={'session_token':session['session_token'],'text':'Explain a fraction.','language':'English'})
    assert response.status_code==200 and response.json()['source']=='PhET Interactive Simulations'
    rejected=client.post('/api/classroom/media',json={'session_token':'x'*32,'text':'Explain a fraction.','language':'English'})
    assert rejected.status_code==401


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
