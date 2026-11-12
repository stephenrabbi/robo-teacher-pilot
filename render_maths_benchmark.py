"""Serve a one-time Maths mouth cue benchmark on a test instance."""
import gzip
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from maths_mouth_cues import prepare_cued_audio


def measure():
    fixture = Path(__file__).with_name("render_maths_benchmark.pcm.gz")
    pcm = gzip.decompress(fixture.read_bytes())
    started = time.monotonic()
    audio, header = prepare_cued_audio(iter([pcm]), os.environ["MATHS_MOUTH_CUE_EXECUTABLE"])
    return {
        "clip_seconds": len(pcm) / 48000,
        "analysis_seconds": round(time.monotonic() - started, 3),
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
