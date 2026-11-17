"""Package a 24 kHz mono PCM WAV and Rhubarb JSON for Maths narration.

Run from the repository root:
    python -m scripts.prepare_maths_narration recording.wav cues.json output/lesson-step
"""
import argparse
import gzip
import json
from pathlib import Path
import wave

from maths_mouth_cues import _MAX_DURATION_SECONDS, _SAMPLE_RATE, _validated_header


def package_narration(recording: Path, cue_file: Path, output: Path) -> None:
    with wave.open(str(recording), "rb") as audio:
        if (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) != (_SAMPLE_RATE, 1, 2):
            raise ValueError("Expected a 24 kHz mono 16-bit PCM WAV")
        frames = audio.getnframes()
        if not 0 < frames <= _MAX_DURATION_SECONDS * _SAMPLE_RATE:
            raise ValueError(f"Expected a non-empty recording of at most {_MAX_DURATION_SECONDS} seconds")
        pcm = audio.readframes(frames)
    if len(pcm) != frames * 2:
        raise ValueError("The WAV contains fewer samples than its header declares")

    cues = json.loads(cue_file.read_text(encoding="utf-8"))
    header = _validated_header(cues, frames / _SAMPLE_RATE)
    if header is None:
        raise ValueError("Expected valid mouthCues within the recording duration")

    audio_path = output.with_name(output.name + ".pcm.gz")
    cues_path = output.with_name(output.name + ".cues.json")
    if audio_path.exists() or cues_path.exists():
        raise ValueError("Choose an unused output name to avoid replacing a recording")
    audio_path.write_bytes(gzip.compress(pcm, mtime=0))
    cues_path.write_text(header + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("recording", type=Path)
    parser.add_argument("cues", type=Path)
    parser.add_argument("output", type=Path, help="Output path prefix in an existing directory")
    args = parser.parse_args()
    try:
        package_narration(args.recording, args.cues, args.output)
    except (OSError, EOFError, ValueError, wave.Error) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
