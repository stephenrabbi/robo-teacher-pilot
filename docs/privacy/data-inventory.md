# Robo-Teacher Data Inventory and Tracking Audit

**Audit date:** 6 October 2026  
**Release target:** v2.6.1

## Browser classroom

Data used:
- nickname (requested instead of full legal name);
- class level;
- learner code;
- pseudonymous learner/session identifier;
- Maths questions and AI answers;
- practice, diagnostic, revision and mastery results;
- progress and recommendations;
- optional image, camera, voice and whiteboard submissions.

Browser-local storage:
- language, speech pace and volume preferences;
- learner continuity/profile mapping;
- saved lessons;
- adaptive teaching memory;
- local classroom snapshot;
- local teacher roster names;
- QA checklist and device timing information.

Local teacher roster names are intentionally kept on the teacher's browser/device and are not sent to the central learner-code service.

## Google Sheets

Private sheets may contain:
- **Student Roster:** pilot ID, school, WhatsApp number or Telegram username for messaging-pilot access, active status and onboarding date.
- **Interaction Log:** timestamp, school, pseudonymous pilot ID, channel, session ID, a short redacted/truncated question excerpt, a short redacted/truncated reply excerpt, status and latency.
- **Learner Profiles:** pseudonymous pilot ID, topic counts, recent-question memory after direct-identifier redaction, explanation preference, difficulty, language preference and update time.
- additional pseudonymous practice/diagnostic/progress records used for teacher support and evaluation.

## Messaging channels

Telegram and the WhatsApp integration/migration path necessarily expose platform identifiers to those platforms. Robo-Teacher uses the identifier to recognise approved pilot learners and route replies.

## Third-party processors/integrations

- Render — application hosting.
- Google Gemini — AI tutoring, image understanding and voice generation.
- Google Sheets — private pilot records.
- Telegram — Telegram bot delivery.
- Twilio — WhatsApp integration/migration path.
- PhET — optional interactive simulation iframe; now blocked until the user allows optional external content.

## Cookies and tracking

No Google Analytics, advertising pixel, behavioural analytics library or cross-site advertising tracker was identified in the v2.6 browser classroom code.

The app uses browser local/session storage for core learning continuity and user preferences. Optional third-party iframe content is consent-gated because the external provider may receive technical data or use cookies/similar storage.

## Data-minimisation changes in v2.6.1

- interaction question/reply excerpts reduced from 500 to 300 characters;
- common email addresses, Nigerian phone numbers, @handles and URLs are redacted before Interaction Log storage;
- learners are explicitly told to use a nickname and avoid entering full names/contact/home-address information;
- third-party simulations do not load until optional external-content consent is granted;
- users can clear Robo-Teacher browser-local data from Privacy choices;
- legal/privacy links are available from the classroom footer;
- no new analytics tracking was added.

## Remaining operational privacy item

The private Student Roster still contains raw WhatsApp numbers or Telegram usernames for messaging-pilot matching. This is a deliberate operational identifier, not public data. A future migration can replace these with stable keyed hashes if messaging-channel continuity is redesigned around a persistent secret and migration plan.
