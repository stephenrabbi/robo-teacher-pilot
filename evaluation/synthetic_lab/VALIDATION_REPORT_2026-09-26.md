# Synthetic Learner Lab — 24-Scenario Validation Report

**Date:** 26 September 2026  
**Branch:** `synthetic-learner-lab-v1`  
**Target:** Robo-Teacher staging only  
**Production changed:** No

## Validation batch

The strengthened validation batch ran 24 balanced synthetic scenarios covering all 12 personas, JSS1-JSS3, the five seed Maths topics, repeated-error behaviour, language/context challenges, and persona-specific probes.

**Observed run totals**
- 24 scenarios
- 78 tutor turns
- 0 scenario errors
- 0 HTTP errors
- 0 adjacent repeated/frozen reply flags
- 0 raw `[ESCALATE]` markers returned to the client

## Latency

Reported tutor latency:
- Median: approximately 2.62 seconds
- Mean: approximately 4.16 seconds
- Maximum: approximately 16.87 seconds
- 46 turns at or below 3 seconds
- 12 turns above 3 and at or below 5 seconds
- 20 turns above 5 seconds

Latency remains the clearest technical concern. The lab now flags >3 seconds as `warning` and >5 seconds as `slow`.

## Mathematical checks

The conservative deterministic checker produced:
- 32 automatic passes
- 2 `review_or_fail` flags
- 13 multilingual cases reserved for human review

Manual inspection showed that the two `review_or_fail` responses were mathematically correct linear-equation explanations; they were false negatives caused by the checker requiring the literal form `x = 5`. The checker has now been widened to recognize clear equivalent statements such as “the correct answer is 5”.

Multilingual responses are intentionally not auto-certified for mathematical or linguistic quality.

## Persona behaviour findings

The new persona probes produced useful differentiated behaviour:
- Low-confidence prompts received encouragement and reteaching.
- Strong learners were given harder or deeper follow-up work.
- Repeated misconceptions generally triggered a different explanation approach.
- An off-topic “football” prompt was redirected toward Maths.
- A request for a real learner's private phone number was refused/redirected rather than answered.

The privacy response was safe, but generic. A future safety refinement could explicitly state that Robo-Teacher does not provide or reveal private personal information.

## Multilingual/context findings

The batch successfully produced Yoruba, Hausa and Igbo responses and several language/context switches preserved the active Maths problem.

However, manual inspection also found language-adherence regressions in persona probes:
- At least one turn requested in English returned primarily Yoruba.
- At least one turn requested in English returned primarily Hausa.
- One English response contained an unexpected Yoruba term.

These are not mathematical failures, but they show that language-state control still needs targeted testing before multilingual behaviour is treated as stable.

## Interpretation

This validation supports the Synthetic Learner Lab as a useful pre-UAT regression layer, but it is not evidence of real learning outcomes and does not replace native-language review or student testing.

Current sequence remains:

`code tests -> synthetic learner lab -> device UAT -> real learner pilot`

## Next recommended technical work

1. Add explicit language-adherence checks and targeted regression cases for mid-session language switching.
2. Add privacy-specific safety scoring so generic out-of-scope handling is distinguished from explicit privacy protection.
3. Investigate staging latency, especially >5-second turns.
4. Keep full 240-scenario execution on hold until language-state and latency issues are better characterized.
5. Keep all work isolated from production while the school pilot is running.
