"""Explicit AI backend selection; never silently switches billing routes."""
import os
from google import genai


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
