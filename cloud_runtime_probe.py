"""Isolated Render smoke test: no learner endpoints and no request-triggered AI calls."""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from google.genai import types
from cloud_ai_provider import create_ai_client, stream_cloud_speech

logger = logging.getLogger('robo-cloud-probe')


def run_probe():
    if os.getenv('ROBO_CLOUD_PROBE_ENABLED') != 'true':
        return {'status': 'disabled'}
    credential_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    if not credential_path or not Path(credential_path).is_file():
        return {'status': 'waiting_for_secret'}
    client = create_ai_client()
    try:
        text = client.models.generate_content(
            model=os.environ['GEMINI_MODEL'],
            contents='Reply with only READY.',
            config=types.GenerateContentConfig(max_output_tokens=128,
                thinking_config=types.ThinkingConfig(thinking_budget=0)))
        if not text.text or not text.text.strip():
            raise ValueError('empty text')
        voice_config = types.GenerateContentConfig(response_modalities=['AUDIO'],
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Kore'))))
        stable = client.models.generate_content(model=os.environ['GEMINI_TTS_MODEL'],
            contents='Say: Welcome to Robo Teacher.', config=voice_config)
        if not any(p.inline_data and p.inline_data.data
                   for c in stable.candidates or [] if c.content
                   for p in c.content.parts or []):
            raise ValueError('empty stable speech')
        chunks = list(stream_cloud_speech(client, os.environ['GEMINI_STREAMING_TTS_MODEL'],
                                         'Say: Welcome to Robo Teacher.', 'Kore'))
        return {'status': 'passed', 'text': True, 'stable_voice': True,
                'stream_chunks': len(chunks), 'stream_bytes': sum(map(len, chunks))}
    finally:
        client.close()


@asynccontextmanager
async def lifespan(app):
    # Once per process start. GET requests can never consume AI credits.
    try:
        app.state.probe = run_probe()
    except Exception as exc:
        # Exception strings and API responses can contain sensitive details.
        app.state.probe = {'status': 'failed', 'error_type': type(exc).__name__}
    logger.warning('CLOUD_RUNTIME_PROBE %s', app.state.probe)
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


@app.get('/health')
def health():
    return getattr(app.state, 'probe', {'status': 'starting'})
