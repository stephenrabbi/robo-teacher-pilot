-- Read-only audit for isolated synthetic project drzaxpofuhqchmpkwhpy.
-- Run through Supabase SQL editor after a synthetic authenticated classroom practice.
-- Do not run against Robo-Teacher production.
select
  count(*) as saved_records,
  count(*) filter (where practice_event_id is not null) as events_with_id,
  count(*) filter (where class_level in ('JSS1','JSS2','JSS3')
    and question_count between 1 and 200
    and correct_count between 0 and question_count
    and completed_at is not null
    and practice_event_id is not null) as fully_enriched_records,
  count(*) filter (where practice_event_id is null) as legacy_records
from public.robo_synthetic_sync_events;
select user_id,score,class_level,question_count,correct_count,completed_at,practice_event_id
from public.robo_synthetic_sync_events
where practice_event_id is not null
order by completed_at desc
limit 10;
