# Lesson checkpoint foundation

Baseline: 5966085, the existing approved responsive redesign release.

This increment preserves the exact lesson step array and nested return bookmarks in the existing device-local snapshot. Both button and voice return paths reuse those checkpoints. Sending a typed interruption stops speech immediately. Changing learner clears lesson and pending-question state.

Validation: 8 Node continuity/checkpoint tests and 16 targeted Python release checks passed. Browser acceptance of this new increment remains pending; earlier production acceptance does not validate these new changes.

Limitations: resumption starts at the beginning of the bookmarked step, not its exact audio timestamp. Drawing/media restoration and a unified presentation state controller are later increments. Device-local snapshots do not implement cross-device identity recovery.

Preview acceptance: interrupt a multi-step lesson, ask a follow-up, return twice, reload during a follow-up, resume and confirm both return destinations. Repeat via voice, then switch learner and confirm that no previous return history or queued question remains.

Rollback: revert the eventual checkpoint commit or redeploy the baseline. No schema or environment changes are required.

## Presentation ownership increment

An in-memory controller issues revision tickets for asynchronous media requests. Asking a question, moving to a lesson, changing stage or clearing learner state revokes previous tickets, preventing stale media success/error responses from taking over the display. This is a first ownership guard, not the complete speech/avatar state machine. Four behavioral controller tests pass; the full Python suite passes 411 tests.

## Speech ownership increment

PCM playback checks its request owner after asynchronous audio preparation and every stream read. A cancelled stream is cancelled without scheduling stale chunks or altering a newer stream completion state. Read-aloud closes an active example and restores the lesson view. Speech/pause states revoke pending media work. Three executable stream-race tests cover delayed chunks, delayed completion and preparation cancellation. Physical audio and full presentation acceptance remain pending.
