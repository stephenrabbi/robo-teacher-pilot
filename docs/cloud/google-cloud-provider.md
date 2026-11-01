# Google Cloud AI provider preparation

The default remains the Developer API. This change enables an explicit Cloud-backed SDK client; it does not prove account eligibility, model availability, voice compatibility or credit application. No APIs, billing settings or credentials are created.

To prepare a preview, verify the target project's billing link, credit eligibility, remaining balance/expiry and model/region access. Use a small synthetic request to verify actual Cloud billing attribution before learner traffic. Do not upgrade a trial account under the user's credit-only instruction.

Configuration for the preview process:

- `ROBO_AI_PROVIDER=vertex`
- `GOOGLE_CLOUD_PROJECT`: verified project ID
- `GOOGLE_CLOUD_LOCATION`: region supported by all selected models
- `GEMINI_MODEL`, `GEMINI_TTS_MODEL`, `GEMINI_STREAMING_TTS_MODEL`: explicitly selected models verified on the Cloud backend
- Application Default Credentials for the intended project; prefer an attached service identity or workload identity. Keep credentials server-side. Do not reuse the Sheets service account without reviewing its role and purpose.

The provider uses the installed google-genai SDK. No Developer API key is passed to the Cloud client. Missing configuration or an unknown provider fails without silently switching backends. The SDK's ambient backend flags cannot switch the default Developer API path.

Run offline: `python -m pytest tests/test_cloud_ai_provider.py -q`.

Preview gates: text request, image question, recorded audio, translation, speech generation and streaming PCM; verify model-specific configuration compatibility and authentication, inspect billing attribution, measure response time and cost, then repeat the interrupted lesson browser journey. The current factory shares one provider for text and speech; split providers in a later increment if eligible Cloud speech models require it.

Rollback: set `ROBO_AI_PROVIDER=developer`, retain the existing `GEMINI_API_KEY`, restore the prior model settings and restart the preview. Existing production remains on its present configuration until separately validated.

References:
- https://googleapis.github.io/python-genai/genai.html
- https://docs.cloud.google.com/docs/authentication/application-default-credentials
- https://docs.cloud.google.com/free/docs/free-cloud-features
- https://ai.google.dev/gemini-api/docs/billing

## Cloud streaming voice adapter (1 November 2026)

When the Cloud backend is explicitly selected, primary streaming speech uses
`models.generate_content_stream` instead of Developer API Interactions. It skips
metadata-only responses, emits audio chunks in order and rejects formats other
than raw 24 kHz PCM, matching the classroom player. The existing Developer route
is unchanged. Cloud candidate models for the preview are `gemini-3.1-flash-lite`,
`gemini-2.5-flash-tts` (stable speech), and `gemini-3.1-flash-tts-preview`
(streaming speech), with location `global`. The stable Cloud TTS model ID differs
from the Developer API default; set it explicitly on the preview only.

User-provided Cloud Shell results confirmed a tiny text request using the runtime
service account on 1 November. This does not verify Render's saved private key,
Cloud speech access, language quality or trial-credit billing attribution. The
temporary impersonation permission was removed after that test. Credentials must
remain in Render secret files; never commit them or include them in test output.

Reference: https://docs.cloud.google.com/text-to-speech/docs/gemini-tts
