"""Trusted local video references for questions; browser supplies only ID/time."""
from functools import lru_cache
from pathlib import Path
import math
import re

_ROOT = Path(__file__).parent / "classroom" / "assets" / "videos"
_VIDEOS = {"rounding-nearest-ten": ("Rounding to the nearest ten — worked example: 47", 41.09)}

@lru_cache(maxsize=8)
def _reference(video_id: str):
    if video_id not in _VIDEOS:
        raise ValueError("Unknown topic video")
    transcript = (_ROOT / f"{video_id}-transcript.txt").read_text().strip()
    captions = (_ROOT / f"{video_id}.vtt").read_text()
    def seconds(stamp):
        h, m, s = stamp.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    cues = tuple((seconds(start), seconds(end), text.replace("\n", " ").strip()) for start, end, text in re.findall(r"(\d\d:\d\d:\d\d\.\d+) --> (\d\d:\d\d:\d\d\.\d+)\n(.*?)(?=\n\n|\Z)", captions, re.S))
    return transcript, cues

def video_question_reference(video_id: str, time: float) -> str:
    if video_id not in _VIDEOS or not math.isfinite(time) or time < 0 or time > 3600:
        raise ValueError("Invalid topic video context")
    title, duration = _VIDEOS[video_id]
    position = min(time, duration)
    transcript, cues = _reference(video_id)
    nearby = " ".join(text for start, end, text in cues if end >= position - 5 and start <= position + 5)
    return (
        f"\n\nTrusted Robo-Teacher video reference (context for the learner's question):\n"
        f"Title: {title}\nPaused position: {position:.2f} seconds\n"
        f"Nearby captions: {nearby}\nComplete transcript: {transcript}\n"
        "Use this reference to explain the video. If the learner's reference is still ambiguous, ask which part they mean. "
        "This reference must never be used to guess an unclear spoken number or claim that the learner said something they did not say."
    )
