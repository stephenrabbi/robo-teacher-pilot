"""Render the directed numbers worked example with Pillow and FFmpeg."""
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw
from build_fractions import text, W, H, INK, BLUE, TEAL, OUT

NAME = "adding-directed-numbers"
SCENES = [
    (8, "What happens when we add negative five to three? Start at three.", 0),
    (5, "Negative five tells us to move five places left.", 0),
    (2, "One.", 1),
    (2, "Two.", 2),
    (2, "Three.", 3),
    (2, "Four.", 4),
    (3, "Five. We land on negative two.", 5),
    (12, "The plus sign tells us to add. The negative sign on five tells us which direction to move.", 5),
    (10, "Start at negative two. Which direction should you move, and where will you land?", None),
]


def frame(index, moves):
    image = Image.new("RGB", (W, H), "#f7faff")
    draw = ImageDraw.Draw(image)
    text(draw, (64, 36), "ROBO-TEACHER  /  WORKED EXAMPLE", 26, TEAL, True)
    text(draw, (64, 104), "Your turn" if moves is None else "Adding directed numbers", 56, bold=True)
    equation = "−2 + 4 = ?" if moves is None else "3 + (−5) = " + ("−2" if moves == 5 else "?")
    text(draw, (640, 210), equation, 76, BLUE, True, "ma")
    positions = {n: 100 + (n + 5) * 108 for n in range(-5, 6)}
    draw.line((65, 420, 1215, 420), fill=INK, width=5)
    for number, x in positions.items():
        draw.line((x, 402, x, 438), fill=INK, width=4)
        text(draw, (x, 455), str(number).replace("-", "−"), 40, anchor="ma")
    for step in range(moves or 0):
        right, left = positions[3 - step], positions[2 - step]
        draw.arc((left, 340, right, 420), 180, 360, fill=TEAL, width=7)
        draw.polygon([(left, 386), (left - 9, 366), (left + 12, 370)], fill=TEAL)
    x = positions[-2 if moves is None else 3 - moves]
    draw.ellipse((x - 15, 405, x + 15, 435), fill=BLUE)
    label = "Which direction? Where will you land?" if moves is None else (
        "Start at 3" if not moves else f"{moves} of 5 moves left"
    )
    if index == 7:
        label = "Adding a negative number moves you left."
    text(draw, (640, 550), label, 43, TEAL, True, "ma")
    return image


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, args)], check=True)


def timestamp(seconds):
    return f"00:{seconds // 60:02}:{seconds % 60:02}.000"


def main():
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        cues = ["WEBVTT", ""]
        start = 0
        for index, (duration, narration, moves) in enumerate(SCENES):
            frame(index, moves).save(temp / f"{index}.png")
            voice = temp / f"{index}.txt"
            voice.write_text(narration)
            ffmpeg("-loop", "1", "-framerate", 12, "-i", temp / f"{index}.png",
                   "-f", "lavfi", "-i", f"flite=textfile={voice}:voice=slt",
                   "-af", "apad", "-t", duration, "-c:v", "libx264",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", temp / f"{index}.mp4")
            cues.extend([f"{timestamp(start)} --> {timestamp(start + duration)}", narration, ""])
            start += duration
        playlist = temp / "segments.txt"
        playlist.write_text("".join(f"file '{i}.mp4'\n" for i in range(len(SCENES))))
        ffmpeg("-f", "concat", "-safe", 0, "-i", playlist, "-c", "copy",
               "-movflags", "+faststart", OUT / f"{NAME}.mp4")
    (OUT / f"{NAME}.vtt").write_text("\n".join(cues))
    (OUT / f"{NAME}-transcript.txt").write_text("\n".join(scene[1] for scene in SCENES) + "\n")


if __name__ == "__main__":
    main()
