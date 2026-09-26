# Robo-Teacher Synthetic Learner Lab v1

This is a **staging-only** evaluation layer inspired by multi-agent simulation ideas. It does not change production Robo-Teacher and it does not use real student data.

## Purpose

Use synthetic learner personas to stress-test Robo-Teacher before new behaviour is exposed to real learners.

The first controlled design contains:

- 12 synthetic learner personas
- JSS1, JSS2 and JSS3
- English, Yoruba, Hausa and Igbo preferences
- 5 Maths topic families
- 4 interaction patterns per topic
- 240 planned interactions in a full run

## Files

- `personas.json` — synthetic learner definitions
- `test_matrix.json` — topics, interaction patterns and evaluation checks
- `run_synthetic_lab.py` — staging API runner

## Safety and measurement rules

1. Use **staging only** by default.
2. Never enter real student names, learner codes, phone numbers, school records or other PII.
3. Synthetic learner IDs must begin with `SL-`.
4. Do not merge this branch into production merely because synthetic tests pass.
5. Synthetic tests are a pre-UAT filter, not evidence of real learning outcomes.
6. Multilingual quality still requires native-language human review.
7. A model response is not automatically correct just because the endpoint returns HTTP 200.

## Run modes

Dry-run only:

```bash
python evaluation/synthetic_lab/run_synthetic_lab.py
```

Small live staging smoke test:

```bash
python evaluation/synthetic_lab/run_synthetic_lab.py --live --max-cases 12
```

Full planned run:

```bash
python evaluation/synthetic_lab/run_synthetic_lab.py --live --full
```

By default the runner targets:

`https://robo-teacher-v25-staging.onrender.com`

Override with:

```bash
ROBO_TEACHER_BASE_URL=https://your-staging-host.example python evaluation/synthetic_lab/run_synthetic_lab.py --live
```

## Output

Results are written locally under `evaluation/synthetic_lab/results/` as JSONL. The results folder should not be committed when it contains generated run data.

## Interpretation

The runner records endpoint success, latency, response length, escalation markers and possible adjacent repeated replies. It intentionally does **not** pretend to automatically judge mathematical correctness, multilingual fluency, safety quality or pedagogical quality. Those require either deterministic checks or human review.

## Relationship to AMASE-MA

This lab can later provide infrastructure for a separate research protocol testing multilingual safety under multi-turn and multi-agent interaction. That research should remain analytically distinct from the current Robo-Teacher pilot.
