"""Confirm mastery from separate answers, not duplicate submissions."""
from unittest.mock import patch
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import classroom_api
import mastery_progress
import retention_progress
from main import app

client = TestClient(app)
TOPIC = 'Fractions, Ratios, Decimals & Percentages'

@pytest.fixture(autouse=True)
def isolated_evidence(monkeypatch):
    classroom_api._classroom_profiles.clear()
    classroom_api._request_times.clear()
    mastery_progress._memory_records.clear()
    mastery_progress._unsynced_ids.clear()
    retention_progress.reset_for_tests()
    monkeypatch.setattr(mastery_progress, '_sheet_configured', lambda: False)
    monkeypatch.setattr(retention_progress, '_sheet_configured', lambda: False)
    yield
    mastery_progress._memory_records.clear()
    mastery_progress._unsynced_ids.clear()
    retention_progress.reset_for_tests()


def session(key='d' * 48):
    response = client.post('/api/classroom/session', json={'nickname':'Synthetic Tester','learner_key':key,'class_level':'JSS2'})
    assert response.status_code == 200
    return response.json()['session_token']


def answer(token, check_id, correct=True, topic=TOPIC):
    response = client.post('/api/classroom/mastery/event', json={'session_token':token,'check_id':check_id,'correct':correct,'stage':'initial','topic_hint':topic,'lesson_text':''})
    assert response.status_code == 200
    return response.json()


def test_two_distinct_successes_confirm_mastery_and_schedule_review():
    token=session()
    first=answer(token,'1'*32)
    assert first['state']=='developing'
    repeated=answer(token,'1'*32)
    assert repeated['state']=='developing'
    assert repeated['summary']['topics'][0]['checks']==1
    second=answer(token,'2'*32)
    assert second['state']=='mastered'
    assert second['summary']['mastered_topics']==[TOPIC]
    assert second['summary']['topics'][0]['checks']==2
    assert second['retention_interval_days']==2
    assert second['next_review_at']
    assert len(mastery_progress._memory_records)==2
    assert mastery_progress._memory_records[-1]["state"]=="mastered"
    restored=client.post('/api/classroom/mastery/summary',json={'session_token':session(),'class_level':'JSS2'})
    assert restored.json()['mastered_topics']==[TOPIC]


def test_wrong_answer_resets_the_confirmation_streak():
    token=session()
    answer(token,'1'*32)
    assert answer(token,'2'*32,False)['state']=='needs_support'
    assert answer(token,'3'*32)['state']=='developing'
    assert answer(token,'4'*32)['state']=='mastered'
    assert answer(token,'5'*32)['state']=='mastered'
    assert answer(token,'6'*32,False)['state']=='needs_support'


def test_evidence_from_another_learner_or_topic_does_not_confirm_mastery():
    token=session()
    answer(token,'1'*32)
    assert answer(session('e'*48),'2'*32)['state']=='developing'
    assert answer(token,'3'*32,topic='Probability')['state']=='developing'


def test_restored_sheet_rows_reconstruct_confirmation_and_deduplicate_events():
    rows=[{'Timestamp (UTC)':f'2026-10-04T15:3{i}:00+00:00','Event ID':str(i)*32,'Learner ID':'synthetic-learner','Learner Code':'TEST-ONLY','Class Level':'JSS2','Topic':TOPIC,'Stage':'initial','Correct':'TRUE','State':'developing'} for i in (1,2)]
    records=[mastery_progress._row_to_record(row) for row in rows]
    result=mastery_progress.summarise_topics(records+[records[-1]])[0]
    assert result['state']=='mastered'
    assert result['checks']==2
    assert result['confidence']=='medium'


def test_autopilot_does_not_create_a_second_event_for_the_same_answer():
    script=Path('classroom/autopilot_session.js').read_text()
    assert "original({...meta, stage: 'reteach'})" not in script
    assert script.count('await original(...args)')==1
