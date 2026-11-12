"""Optional offline mouth timing for short Maths narration."""
import json
import subprocess
import tempfile
import wave
from itertools import chain
from pathlib import Path
from threading import BoundedSemaphore

_SAMPLE_RATE = 24_000
_MAX_AUDIO_BYTES = _SAMPLE_RATE * 2 * 8
_ANALYSER_SLOT = BoundedSemaphore(1)


def prepare_cued_audio(chunks, executable):
    """Return the original PCM and, when available, its validated cue header."""
    if not executable or not _ANALYSER_SLOT.acquire(blocking=False):
        return chunks, None
    try:
        buffered = bytearray()
        for chunk in chunks:
            if len(buffered) + len(chunk) > _MAX_AUDIO_BYTES:
                return chain((bytes(buffered), chunk), chunks), None
            buffered.extend(chunk)
        pcm = bytes(buffered)
        return iter((pcm,)), _mouth_cue_header(pcm, executable)
    finally:
        _ANALYSER_SLOT.release()


def _mouth_cue_header(pcm, executable):
    if not pcm or len(pcm) % 2:
        return None
    try:
        with tempfile.TemporaryDirectory(prefix="robo-maths-mouth-") as folder:
            audio = Path(folder) / "speech.wav"
            output = Path(folder) / "cues.json"
            with wave.open(str(audio), "wb") as wav:
                wav.setparams((1, 2, _SAMPLE_RATE, 0, "NONE", "not compressed"))
                wav.writeframes(pcm)
            subprocess.run(
                [executable, "-q", "-r", "phonetic", "--threads", "1", "-f", "json", "-o", str(output), str(audio)],
                check=True, timeout=3, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if output.stat().st_size > 16_000:
                return None
            data = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return _validated_header(data, len(pcm) / (_SAMPLE_RATE * 2))


def _validated_header(data, duration):
    cues = data.get("mouthCues") if isinstance(data, dict) else None
    if not isinstance(cues, list) or not 1 <= len(cues) <= 240:
        return None
    previous_end = 0
    for cue in cues:
        if not isinstance(cue, dict) or set(cue) != {"start", "end", "value"}:
            return None
        start, end, value = cue["start"], cue["end"], cue["value"]
        if type(start) not in (int, float) or type(end) not in (int, float):
            return None
        if not (previous_end <= start < end <= duration) or value not in tuple("ABCDEFGHX"):
            return None
        previous_end = end
    header = json.dumps(cues, separators=(",", ":"), ensure_ascii=True)
    return header if len(header) <= 4_000 else None
