# Synthetic Learner Lab v1 — Current Validation Status

**Date:** 26 September 2026  
**Branch:** `synthetic-learner-lab-v1`  
**Isolated Render service:** `robo-teacher-synthetic-lab`  
**Production changed:** No  
**School-pilot staging changed:** No

## What is verified

- The isolated Render service deploys successfully from the experimental branch.
- Classroom session creation works on the isolated service.
- The Synthetic Learner Lab runner can execute balanced and targeted scenarios against the isolated host.
- Deterministic fraction tutoring still works correctly on the isolated service.
- The runner now:
  - separates HTTP failures from tutor/model quota fallbacks,
  - excludes quota fallback text from Maths, language, privacy, and repetition scoring,
  - marks a run invalid for quality analysis when any model turn remains rate-limited,
  - supports a targeted language/privacy gate,
  - keeps generated result files out of source control.

## Current blocker: model quota

The latest targeted four-scenario gate contained 12 tutor turns.

Observed:
- 1 deterministic turn completed normally and passed the Maths check.
- 11 model-dependent turns returned Robo-Teacher's friendly rate-limit fallback.
- 0 HTTP errors occurred.
- The runner correctly marked all 11 quota-limited turns as **not scored**.
- The complete run was correctly marked **not valid for quality analysis**.

Therefore, the current blocker is not the Synthetic Learner Lab code or Render deployment. The blocker is model availability/quota for the configured Gemini model/API key.

No claims about language switching, privacy behaviour, multilingual quality, or non-deterministic Maths quality should be made from this quota-limited gate.

## Earlier 24-scenario batch correction

An earlier 24-scenario isolated batch appeared to contain many repeated replies and Maths-review flags. Inspection showed that a large share were actually the same friendly model rate-limit fallback. Those counts must not be interpreted as product-quality failures.

The runner has now been corrected so future summaries do not count quota fallbacks as:
- repeated/frozen tutor replies,
- mathematical failures,
- language failures,
- privacy failures.

## Release gate still required

Before Synthetic Learner Lab v1 can be frozen as complete, run the targeted gate when model quota is available and require:

1. no HTTP errors;
2. no unresolved model rate-limit turns;
3. English -> Yoruba/Hausa/Igbo and local-language -> English switches retain Maths context;
4. no private personal information disclosure;
5. no frozen/repeated tutor answer;
6. deterministic seed Maths checks pass;
7. multilingual responses are retained for native-language review rather than falsely auto-certified.

After the targeted gate passes, run the 24-scenario validation. Only then proceed to the 240-scenario full batch.

## Evidence discipline

Synthetic evaluation is a regression-testing layer. It is not evidence of real student learning outcomes and does not replace device UAT, native-language review, or the school pilot.
