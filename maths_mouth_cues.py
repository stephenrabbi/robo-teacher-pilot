"""Load audio and cues prepared together for a known Maths narration."""
import gzip
import json
from functools import lru_cache
from pathlib import Path

_SAMPLE_RATE = 24_000
_NARRATION_DIR = Path(__file__).with_name("classroom_narration")
_PREPARED = {("Add two to both sides of the equation.", "English", "female", "normal"): "add-two-both-sides"}


def prepared_maths_narration(text, language, voice_gender, pace):
    key = _PREPARED.get((text, language, voice_gender, pace))
    return _load_prepared(key) if key else None


@lru_cache(maxsize=len(_PREPARED))
def _load_prepared(key):
    try:
        with gzip.open(_NARRATION_DIR / f"{key}.pcm.gz", "rb") as audio:
            pcm = audio.read(_SAMPLE_RATE * 2 * 8 + 1)
        cues = json.loads((_NARRATION_DIR / f"{key}.cues.json").read_text(encoding="utf-8"))
    except (OSError, EOFError, ValueError):
        return None
    if not pcm or len(pcm) % 2 or len(pcm) > _SAMPLE_RATE * 2 * 8:
        return None
    header = _validated_header({"mouthCues": cues}, len(pcm) / (_SAMPLE_RATE * 2))
    return (pcm, header) if header else None


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
