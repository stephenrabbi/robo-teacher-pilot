# Classroom 2.0 Welcome — Visual QA Review (21 Oct 2026)

## Evidence
GitHub Actions run: https://github.com/stephenrabbi/robo-teacher-pilot/actions/runs/39641925732
Screenshot artifact: https://github.com/stephenrabbi/robo-teacher-pilot/actions/runs/39641925732/artifacts/12364208514

## Tested browser sizes
- Chromium 320px — full-page screenshot 320 x 2615
- Chromium 375px — full-page screenshot 375 x 2441
- Chromium 768px — full-page screenshot 768 x 1931
- Chromium 1366px — full-page screenshot 1366 x 1280

## Visual observations
1. Student photograph and founder portrait render at the top of the welcome page in all four screenshots.
2. Welcome introduction, onboarding, actions and how-to guide appear in the intended responsive reading order.
3. The privacy-choice prompt overlaps the onboarding area on first load; particularly notable at tablet width. Assess whether the panel should be repositioned, collapsed or otherwise made less obstructive, while preserving the existing privacy/compliance decisions.
4. Mobile full-page layouts are tall (2,441–2,615px). Review whether the learner can find Start Learning Now, Hear Herbert and the permission checkbox without undue scrolling; avoid merely hiding legally required content.
5. The desktop welcome page is compact and two-column, but its design alignment still merits a human review.

## Test limitations
- Screenshots were taken by headless Chromium, not a physical Android phone.
- The backend was simulated for the successful onboarding browser test.
- Voice sound, actual founder talking animations, microphone, camera, keyboard and end-to-end learner sessions have not been device-verified.
- Privacy prompts must continue to function correctly and should not be silently dismissed or bypassed for users.
- These findings do not authorize merging or deploying.

## Hosting review
The existing Render service robo-teacher-supabase-classroom-test uses the staging/supabase-classroom-sync-oct19 branch, with automatic deployment off and pull-request previews disabled. This branch must not be repointed or deployed to for the Classroom 2.0 preview without a separate explicit decision.
