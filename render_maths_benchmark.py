"""Serve a one-time Maths mouth cue benchmark on a test instance."""
import gzip
import json
import os
import time
import subprocess
import tempfile
import wave
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from maths_mouth_cues import prepare_cued_audio


def measure():
    fixture = Path(__file__).with_name("render_maths_benchmark.pcm.gz")
    pcm = gzip.decompress(fixture.read_bytes())
    started = time.monotonic()
    audio, header = prepare_cued_audio(iter([pcm]), os.environ["MATHS_MOUTH_CUE_EXECUTABLE"])
    bounded_seconds = round(time.monotonic() - started, 3)
    with tempfile.TemporaryDirectory() as folder:
        wav_path = Path(folder) / "sample.wav"
        cue_path = Path(folder) / "cues.json"
        with wave.open(str(wav_path), "wb") as wav:
            wav.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
            wav.writeframes(pcm)
        started = time.monotonic()
        try:
            subprocess.run([os.environ["MATHS_MOUTH_CUE_EXECUTABLE"], "-q", "-r", "phonetic", "--threads", "1", "-f", "json", "-o", str(cue_path), str(wav_path)], timeout=15, check=True, capture_output=True)
            extended_cues = len(json.loads(cue_path.read_text())["mouthCues"])
            extended_status = "completed"
        except subprocess.TimeoutExpired:
            extended_cues = 0
            extended_status = "timed out"
        except subprocess.CalledProcessError as error:
            extended_cues = 0
            extended_status = f"exit {error.returncode}"
        extended_seconds = round(time.monotonic() - started, 3)
    return {
        "extended_status": extended_status,
        "extended_seconds": extended_seconds,
        "extended_cues": extended_cues,
        "clip_seconds": len(pcm) / 48000,
        "analysis_seconds": bounded_seconds,
        "cues": len(json.loads(header)) if header else 0,
        "pcm_preserved": b"".join(audio) == pcm,
    }


if __name__ == "__main__":
    result = json.dumps(measure()).encode()
    print(result.decode(), flush=True)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(result)))
            self.end_headers()
            self.wfile.write(result)

    HTTPServer(("0.0.0.0", int(os.environ["PORT"])), Handler).serve_forever()
