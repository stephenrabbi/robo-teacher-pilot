"""Isolated Render smoke test: no learner endpoints and no request-triggered AI calls."""
import logging
import os
import re
import struct
import zlib
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from google.genai import types
from cloud_ai_provider import create_ai_client, stream_cloud_speech

logger = logging.getLogger('robo-cloud-probe')


def triangle_image():
    """Generate a synthetic triangle PNG without files or extra dependencies."""
    size = 96
    pixels = [bytearray([255] * size) for _ in range(size)]
    for y in range(16, 81):
        left = 48 - (y - 16) // 2
        right = 48 + (y - 16) // 2
        for x in (left, left + 1, right - 1, right):
            pixels[y][x] = 0
    pixels[80][16:81] = bytes(65)
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', size, size, 8, 0, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b''.join(b'\0' + row for row in pixels))) + chunk(b'IEND', b''))


def run_extended_probe():
    """Exercise real tutoring entry points with synthetic content only."""
    import tutor
    result = {}
    checks = {
        'image_question': lambda: tutor.get_tutor_image_reply(
            'TEST-CLOUD-MEDIA', triangle_image(), 'image/png',
            'How many sides does the shape have?')[0],
        'audio_question': lambda: tutor.get_tutor_audio_reply(
            'TEST-CLOUD-MEDIA', tutor.generate_tutor_speech('What is two plus three?'), 'audio/wav')[0],
    }
    for name, action in checks.items():
        try:
            answer = action()
            expected = r'\b(3|three)\b' if name == 'image_question' else r'\b(5|five)\b'
            result[name] = bool(re.search(expected, answer, re.I))
        except Exception as exc:
            result[name] = {'error_type': type(exc).__name__}
    for language in ('Yoruba', 'Igbo', 'Hausa'):
        try:
            answer = tutor.translate_tutor_text('Add the numbers: 2 + 3 = 5.', language)
            result['translation_' + language.lower()] = bool(answer.strip() and '2 + 3 = 5' in answer)
        except Exception as exc:
            result['translation_' + language.lower()] = {'error_type': type(exc).__name__}
    return result


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
        extended = run_extended_probe()
        return {'status': 'passed' if all(value is True for value in extended.values()) else 'partial',
                'text': True, 'stable_voice': True, 'extended': extended,
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
