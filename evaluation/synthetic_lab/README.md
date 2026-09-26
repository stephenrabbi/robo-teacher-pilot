# Robo-Teacher Synthetic Learner Lab v1

This is a **staging-only** evaluation layer. It does not change production Robo-Teacher and it does not use real student data.

## Purpose

Use synthetic learner personas to stress-test Robo-Teacher before new behaviour reaches real learners.

The design contains 12 personas across JSS1-JSS3, four language preferences, five Maths topic families, and four interaction patterns. This gives **240 synthetic scenarios**. Each scenario contains 2-3 tutor turns so context retention, misconception correction, reteaching, and language switching are tested as conversations rather than isolated prompts.

## Files

- `personas.json` — 12 synthetic learner definitions
- `test_matrix.json` — topics, interaction patterns, and evaluation checks
- `run_synthetic_lab.py` — staging API runner
- `.gitignore` — prevents generated JSONL results from being committed accidentally

## Safety and measurement rules

1. Use **staging only**.
2. Never use real student names, learner codes, phone numbers, school records, or other personal data.
3. Synthetic IDs begin with `SL-`.
4. Each scenario uses an isolated synthetic learner key; multi-turn messages inside that scenario share one session.
5. Synthetic tests are a pre-UAT filter, not evidence of real learning outcomes.
6. Multilingual quality still requires native-language review.
7. HTTP success does not prove mathematical or pedagogical correctness.
8. Do not merge into production merely because synthetic tests pass.

## Run modes

Dry run:

```bash
python evaluation/synthetic_lab/run_synthetic_lab.py
```

Small staging smoke test:

```bash
python evaluation/synthetic_lab/run_synthetic_lab.py --live --max-cases 12
```

Full run:

```bash
python evaluation/synthetic_lab/run_synthetic_lab.py --live --full
```

Default host:

`https://robo-teacher-v25-staging.onrender.com`

The runner refuses a live run when the configured base URL does not look like a staging host.

## Output

Generated results are written under `evaluation/synthetic_lab/results/` as JSONL. Review results before committing or sharing them.

The runner records HTTP status, wall-clock latency, provider-reported latency, response length, escalation markers, and possible adjacent repeated replies. Mathematical correctness, multilingual fluency, safety quality, and teaching quality still need deterministic checks and/or human review.

## Evaluation sequence

`code tests -> synthetic learner lab -> device UAT -> real learner pilot`

## AMASE-MA

This lab can later support a separate research protocol on multilingual safety under multi-turn and multi-agent interaction. AMASE-MA should remain analytically separate from current Robo-Teacher pilot evidence.
