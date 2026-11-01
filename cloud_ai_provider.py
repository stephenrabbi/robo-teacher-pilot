"""Explicit AI backend selection; never silently switches billing routes."""
import os
from google import genai
from google.genai import types
import base64


def cloud_backend_selected():
    return os.getenv('ROBO_AI_PROVIDER', 'developer').strip().lower() == 'vertex'


def stream_cloud_speech(client, model, prompt, voice):
    """Use Cloud generateContent streaming, returning only 24 kHz mono PCM."""
    stream = client.models.generate_content_stream(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['AUDIO'],
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))),
        ),
    )
    emitted = False
    for response in stream:
        for candidate in response.candidates or []:
            for part in (candidate.content.parts or []) if candidate.content else []:
                audio = part.inline_data
                if not audio or not audio.data:
                    continue
                mime = (audio.mime_type or '').lower().replace(' ', '')
                if mime not in ('audio/l16;codec=pcm;rate=24000', 'audio/pcm;rate=24000',
                                'audio/l16;rate=24000'):
                    raise ValueError('Cloud speech returned an unsupported PCM format')
                pcm = base64.b64decode(audio.data, validate=True) if isinstance(audio.data, str) else bytes(audio.data)
                if pcm:
                    emitted = True
                    yield pcm
    if not emitted:
        raise RuntimeError('Cloud speech returned no audio')


def create_ai_client():
    provider = os.getenv('ROBO_AI_PROVIDER', 'developer').strip().lower()
    if provider == 'developer':
        # Explicit flags prevent ambient SDK environment switches changing billing.
        return genai.Client(enterprise=False, vertexai=False,
                            api_key=os.environ['GEMINI_API_KEY'])
    if provider != 'vertex':
        raise ValueError('ROBO_AI_PROVIDER must be developer or vertex')
    required = ('GOOGLE_CLOUD_PROJECT', 'GOOGLE_CLOUD_LOCATION', 'GEMINI_MODEL',
                'GEMINI_TTS_MODEL', 'GEMINI_STREAMING_TTS_MODEL')
    missing = [key for key in required if not os.getenv(key, '').strip()]
    if missing:
        raise ValueError('Cloud AI configuration missing: ' + ', '.join(missing))
    # Use ADC: no Developer API key is passed to the Cloud endpoint.
    return genai.Client(enterprise=True, vertexai=True,
                        project=os.environ['GOOGLE_CLOUD_PROJECT'].strip(),
                        location=os.environ['GOOGLE_CLOUD_LOCATION'].strip())
