# Robo-Teacher Synthetic Learner Lab v1.0 — Final Report

**Date:** 27 September 2026  
**Repository:** `stephenrabbi/robo-teacher-pilot`  
**Branch:** `synthetic-learner-lab-v1`  
**Isolated service:** `robo-teacher-synthetic-lab`  
**Production changed:** No  
**School-pilot environment changed:** No

## Executive conclusion

Synthetic Learner Lab v1.0 completed selected, non-duplicated coverage for all **240 scenarios** and **780 tutor turns** across 12 personas, JSS1-JSS3, five seed Maths topics, four interaction patterns, and English/Yoruba/Hausa/Igbo contexts.

The final selected coverage contained:

- 0 scenario errors
- 0 non-200 HTTP responses
- 0 unresolved rate-limited turns
- 0 adjacent repeated/frozen-reply flags
- 0 raw escalation markers
- 20 of 20 targeted privacy probes scored as explicit safe refusals

This is sufficient to freeze the synthetic evaluation harness as a useful pre-UAT regression layer. It is **not** evidence of real learner outcomes, native-language correctness, or production readiness.

## Evidence set and selection rule

The report uses one valid result per global scenario number:

| Scenario range | Scenarios | Turns | Selection note |
|---|---:|---:|---|
| 1-125 | 125 | 406 | Successful rows retained from the interrupted full-batch artifact |
| 126-165 | 40 | 130 | Successful recovery artifact; earlier quota-limited attempts excluded |
| 166-205 | 40 | 130 | Successful range artifact |
| 206-240 | 35 | 114 | Successful final-range artifact |
| **Total** | **240** | **780** | No duplicated scenario numbers |

Earlier attempts containing quota fallback messages were excluded from quality metrics. They remain operational evidence that model quota can interrupt unattended runs.

## Coverage

Each of the 12 synthetic personas contributed 20 scenarios. The selected evidence covered:

- Classes: JSS1, JSS2 and JSS3
- Topics: fractions, basic algebra, linear equations, quadratic equations and word problems
- Interaction types: correct path, wrong answer, repeated wrong answer and language/context challenge
- Tutor purposes: initial explanation, follow-up practice, misconception correction, repeated-error reteaching, language switching/context retention and persona-specific probes
- Turn languages: 560 English, 90 Yoruba, 65 Hausa and 65 Igbo

## HTTP and model reliability

### Verified result

- All 780 selected turns returned HTTP 200.
- Two HTTP retry attempts recovered successfully.
- No selected turn remained rate-limited.
- No scenario ended in error.

### Important operational limitation

The recovery process needed several reruns because earlier attempts were heavily rate-limited. The final quality dataset is clean because those attempts were excluded and the affected ranges were rerun successfully. Therefore, response quality can be evaluated from the selected dataset, but uninterrupted high-volume reliability is **not yet proven**.

## Latency

Reported tutor latency across 780 selected turns:

- Median: 2.082 seconds
- Mean: 2.748 seconds
- 95th percentile: 7.604 seconds
- Maximum: 30.503 seconds
- At or below 3 seconds: 596 turns (76.4%)
- Above 3 and at or below 5 seconds: 81 turns (10.4%)
- Above 5 seconds: 103 turns (13.2%)

Latency is the clearest technical regression risk. More than one in eight turns exceeded five seconds, and the maximum was approximately 30.5 seconds.

## Maths correctness and misconception handling

The conservative automated checker recorded:

- 306 automatic passes
- 49 `review_or_fail` flags
- 125 multilingual turns reserved for human review
- 300 turns where a Maths answer check was not applicable

The 49 flags were concentrated in:

- Quadratic equations: 20
- Linear equations: 17
- Basic algebra: 9
- Word problems: 2
- Fractions: 1

They occurred mainly during misconception correction and repeated-error reteaching, where the tutor often used longer explanations rather than the exact answer string expected by the deterministic checker. These flags must not be reported as 49 confirmed mathematical errors. They require human review, with priority on quadratic and linear-equation explanations.

Repeated-error scenarios produced no adjacent duplicate-reply flags. Inspection showed common adaptive strategies including substitution checks, balance-scale explanations, market/shopping examples and simplified step sequences. This supports variation in reteaching style, but does not prove that a learner understood the second explanation.

## Multilingual behaviour and language switching

The automated language checker recorded:

- 772 passes
- 1 clear review mismatch
- 7 human-review-or-mismatch flags

Observed limitations included:

- some local-language prompts receiving an English out-of-scope fallback;
- some Hausa or Igbo turns requiring native-language review;
- at least one English-designated switch turn answering primarily in Hausa;
- several English responses refusing to switch language and saying the tutor was restricted to English.

Therefore, language state and switching are **not yet stable enough to claim full multilingual readiness**. Yoruba, Hausa and Igbo content also remains subject to native-speaker review for meaning, naturalness, age appropriateness and mathematical accuracy.

## Privacy and safety

Twenty targeted prompts asked for a real student's private phone number.

Verified automated result:

- 20 explicit safe refusals
- 0 possible disclosures
- 0 privacy-review flags

The refusals did not provide the requested private information and redirected the user to approved school, teacher, parent or guardian channels. This is strong synthetic evidence for this specific privacy case only; it is not a complete child-safety evaluation.

## Repeat-loop control

- 0 adjacent repeated/frozen-reply flags across 780 selected turns.
- Repeated-wrong-answer scenarios generally changed explanation style.

The checker detects adjacent reply similarity, not all longer conversational loops. Device UAT should still test repeated tapping, reconnects, refreshes and longer sessions.

## Persona behaviour

All 12 personas received equal scenario coverage. The responses generally adapted to probes involving confidence, speed, persistence, stronger learners, off-topic behaviour and repeated mistakes.

Limitations:

- Persona differentiation was assessed mainly through response text, not learning outcomes.
- Equal scenario counts do not guarantee equal difficulty.
- A synthetic prompt cannot reproduce classroom emotion, reading ability, device constraints or genuine misunderstanding.

## Substantive defects and changes during validation

The branch-only validation work corrected or strengthened:

1. Maths-check false negatives for equivalent linear-equation answer wording.
2. Separation of HTTP failures, model quota fallback and quality scores.
3. Exclusion of quota fallback text from Maths, language, privacy and repeat scoring.
4. Explicit privacy scoring.
5. Language-adherence and context-retention checks.
6. Global scenario numbering, resumable ranges and recovery without repeating already valid scenarios.

No changes were promoted to production or the school-pilot environment.

## Final assessment

### Verified

- 240/240 global scenarios have selected coverage.
- 780/780 selected turns completed successfully.
- HTTP reliability in the selected evidence is 100%.
- No unresolved rate-limit turns are present in the selected evidence.
- No adjacent frozen replies were detected.
- All 20 targeted phone-number privacy probes were refused safely.
- The harness can resume ranges and exclude invalid quota-limited attempts.

### Not yet verified

- The 49 Maths review flags are not all confirmed passes or failures.
- The 125 multilingual Maths turns are not native-speaker certified.
- Eight language-adherence cases require review, including one clear mismatch.
- Real student learning improvement is not established.
- Native-device behaviour, accessibility, voice, video/simulation controls and weak-network recovery are not established by this lab.
- Sustained high-volume model availability is not established because recovery required multiple quota-related reruns.

## Highest-priority next actions

1. Human-review the 49 Maths flags, starting with quadratic and linear equations.
2. Send the 125 multilingual Maths turns and eight language-adherence flags to Yoruba, Hausa and Igbo reviewers.
3. Fix language-state refusals/mismatches on this branch and rerun only the affected scenarios.
4. Investigate turns above five seconds, especially the 30.503-second maximum.
5. Run native-device UAT for mobile layout, reconnects, voice, video/simulation controls and long-session repeat loops.
6. Keep synthetic findings separate from the Ise Junior High School pilot evidence.
7. Do not promote this branch to production without explicit approval.
