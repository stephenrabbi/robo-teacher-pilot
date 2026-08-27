# Robo-Teacher JSS2 Mathematics Post-Assessment

**Purpose:** Measure change in Mathematics performance after the defined Robo-Teacher pilot period.

**Administration:** Use the same 20 questions as the baseline assessment, under comparable conditions. Administer after the defined pilot period, not immediately after a tutoring session. Record the actual administration date.

**Important:** The assessment instrument is intentionally identical to the baseline so that scores are directly comparable. Do not provide students with the answer key before or during administration.

## Scoring structure

- 1 point per question.
- Maximum score: 20 points.
- Percentage = `(score / 20) × 100`.
- Record results using Pilot ID rather than student name.
- Keep the private roster containing names/contact identifiers separate from evaluation results.

## Questions

Use questions 1–20 from `evaluation/BASELINE_ASSESSMENT.md` without changing wording, order, or answer choices.

## Post-assessment data capture

For each participant record:

| Field | Description |
|---|---|
| Pilot ID | Anonymous/pseudonymous participant identifier |
| School | Ise or Tio pilot school |
| Assessment date | Actual post-assessment date |
| Score | Number correct, 0–20 |
| Percentage | Score ÷ 20 × 100 |
| Baseline score | Matched baseline score, when available |
| Score change | Post-test score − baseline score |
| Percentage-point change | Post-test percentage − baseline percentage |
| Administration notes | Optional notes about testing conditions |

Do not put student names, phone numbers, Telegram usernames, or other direct contact identifiers in this evaluation table.

## Matched pre/post analysis

Only calculate individual learning change for students who have both a valid baseline and valid post-assessment score.

For each matched participant:

`Score change = Post score − Baseline score`

`Percentage-point change = Post percentage − Baseline percentage`

Group measures should include:

- Number of matched students (`n`)
- Mean baseline score
- Mean post-assessment score
- Mean score change
- Mean baseline percentage
- Mean post-assessment percentage
- Mean percentage-point change
- Median score change
- Number and percentage of students whose score increased
- Number and percentage whose score stayed the same
- Number and percentage whose score decreased

## Interpretation rules

- Report the observed pre/post change accurately.
- Do not describe the change as causal proof that Robo-Teacher caused the improvement unless the study design supports that claim.
- Report the number of students included in the matched analysis.
- Do not exclude inconvenient results without documenting the reason.
- If baseline and post-assessment conditions differed materially, record that limitation.

## Assessment integrity

The post-assessment should be administered under conditions reasonably comparable to the baseline: same 20 questions, similar time allowance, independent student work, and no access to the answer key.

The post-assessment is an evaluation instrument, not a tutoring interaction. Do not send the test questions through Robo-Teacher immediately before the assessment in a way that could compromise comparability.

## Relationship to baseline

The baseline instrument and answer key are maintained in `evaluation/BASELINE_ASSESSMENT.md`. The analysis methodology is documented in `evaluation/ANALYSIS_TEMPLATE.md` and the aggregate reporting structure in `evaluation/PILOT_DASHBOARD.md`.
