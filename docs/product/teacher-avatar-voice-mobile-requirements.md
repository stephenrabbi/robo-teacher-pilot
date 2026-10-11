# Robo-Teacher: learner-selected avatar, voice and mobile teaching requirements

Status: product vision and acceptance criteria. This document does **not** establish that all features are deployed or verified.

## Experience
Every learner should be able to choose their own AI teacher avatar and teaching voice independently, then converse naturally about education on a mobile phone at any time, subject to internet connectivity, platform availability and safeguarding requirements. The teacher should explain with images, diagrams, infographics, video, animation and whiteboard content without blocking the content or interrupting instruction.

## Functional requirements and verification criteria

1. **Teacher avatar selection:** Offer a clear accessible selection flow; support at least two distinguishable avatars in testing; remember learner-specific selection without exposing another learner's preferences on a shared device. Test selection and resume on mobile and desktop.
2. **Independent voice selection:** Learners can choose among available voices independent of the avatar; provide speech speed, mute and playback controls. Verify output matches the selected voice and continues consistently across lessons. Fall back visibly when voice service is unavailable; do not silently claim voice switching worked.
3. **Automatic minimise/restore:** When video, diagram, infographic, animation, image or a teaching canvas needs space, avatar collapses into a small non-obstructive movable/dockable view. When visual teaching concludes or the teacher resumes direct speaking, avatar can expand. Include manual minimise/maximise; no unexpected overlay on answer input or visuals.
4. **Lesson continuity:** Minimising/restoring must not erase lesson progress, duplicate utterances, restart explanations, stop a currently playing relevant visual unexpectedly or lose conversation context. Test rapid transitions and interruptions.
5. **Conversational teaching:** Typed and voice questions, spoken and written explanations, follow-up questions and clarification requests work from phones. Education-focused guardrails and age-appropriate content; escalate to a human teacher or guardian where appropriate.
6. **Mobile availability:** Responsive layout supports common Android and iPhone viewport sizes and browser input; clearly distinguish 24/7 intended access from service uptime guarantees. Test keyboard, microphone/camera permission denial, poor connectivity, and playback recovery.
7. **Accessibility and language:** Keyboard and screen reader controls, captions/transcripts for spoken instruction where feasible, contrast, touch targets, selected language persistence, and test switching among supported languages.
8. **Account separation:** Preferences, chat history and progress must be bound to verified learner identity when sync is enabled, isolated when multiple pupils use the same device, and protected by the privacy/consent rules for minors.

## Example end-to-end acceptance journey
- Learner opens the mobile classroom and signs in or enters through an approved learner flow.
- Learner selects an avatar and a voice, then asks for help with a Mathematics topic.
- Avatar explains; when the lesson displays a diagram/video, it automatically minimises while narration and context continue.
- Learner asks a follow-up and works on the whiteboard; avatar expands when appropriate without restarting the teaching sequence.
- Learner leaves and returns; settings and learning continuity are restored for the correct learner, not another learner using the same phone.
- Network and microphone permission failures produce recoverable, truthful statuses without losing saved work.

## Delivery gates
- Audit the current production features; label each requirement verified, partial, not implemented or blocked.
- Build behind flags on an isolated branch; test synthetic accounts and no real pupil identifiers.
- Test desktop, Android and iPhone user journeys, accessibility and low-connectivity recovery before broader rollout.
- Keep actual subject coverage distinct from the all-subject vision: working JSS1–JSS3 Mathematics is the current documented implementation; wider subjects are future expansion.

Product principle: **Every learner. Their own AI teacher.**
