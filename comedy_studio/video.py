"""Render original illustrated scenes and encode an H.264/AAC vertical MP4."""
from __future__ import annotations

import json
import math
import re
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH, HEIGHT = 720, 1280
FPS = 24
DURATION_PER_SCENE = 3.0
INK = "#18243B"
PALETTE = ["#F8C96A", "#77C9C4", "#A7B5F4", "#F7A79A"]
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _wrapped(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        attempt = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), attempt, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = attempt
    if current:
        lines.append(current)
    return lines


def _center_text(draw: ImageDraw.ImageDraw, text: str, y: int, font: Any, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((WIDTH - (box[2] - box[0])) / 2, y), text, font=font, fill=fill)


def _background(image: Image.Image, room: str, scene_index: int) -> None:
    draw = ImageDraw.Draw(image)
    colors = [("#FFF2D9", "#F6D8C4"), ("#DFF5F0", "#C4E4DD"),
              ("#E9EEFF", "#D5D9F1"), ("#FFF0E8", "#EACCCC")]
    top, bottom = colors[scene_index % len(colors)]
    a = tuple(int(top[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(bottom[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = tuple(round(a[k] * (1 - t) + b[k] * t) for k in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    # Soft graphic sun and room floor give the scene depth without external artwork.
    draw.ellipse((530, 160, 650, 280), fill="#FFE29B")
    draw.rectangle((0, 800, WIDTH, 880), fill="#C99575")
    draw.rectangle((0, 880, WIDTH, HEIGHT), fill="#E8CBB7")
    for x in (40, 680):
        draw.ellipse((x - 5, 315, x + 5, 325), fill="#FFFFFF")
        draw.ellipse((x - 3, 370, x + 3, 376), fill="#FFFFFF")
    room_tag = room.replace("-", " ").upper()
    tag_font = _font(18, True)
    draw.rounded_rectangle((38, 266, 38 + max(126, draw.textbbox((0, 0), room_tag, font=tag_font)[2] + 36), 306), 18, fill="#FFFFFF")
    draw.text((56, 276), room_tag, font=tag_font, fill="#647089")


def _draw_person(draw: ImageDraw.ImageDraw, x: int, y: int, phase: float, color: str, expression: str) -> None:
    # Animated, friendly character assembled entirely from original vector-like shapes.
    bounce = int(math.sin(phase * math.pi * 2) * 5)
    y += bounce
    draw.ellipse((x - 73, 798, x + 82, 822), fill="#BC927C")
    # Legs and shoes
    draw.line((x - 22, y + 147, x - 35, y + 212), fill="#354967", width=20)
    draw.line((x + 24, y + 147, x + 38, y + 212), fill="#354967", width=20)
    draw.rounded_rectangle((x - 61, y + 199, x - 20, y + 217), 8, fill="#26324A")
    draw.rounded_rectangle((x + 18, y + 199, x + 61, y + 217), 8, fill="#26324A")
    # Arms, torso, face, hair
    draw.line((x - 43, y + 47, x - 91, y + 105 + int(math.sin(phase * 4) * 6)), fill="#E6A27E", width=20)
    draw.line((x + 43, y + 47, x + 89, y + 96), fill="#E6A27E", width=20)
    draw.rounded_rectangle((x - 52, y + 28, x + 52, y + 157), 32, fill=color)
    draw.ellipse((x - 47, y - 56, x + 47, y + 43), fill="#F1B890")
    draw.pieslice((x - 49, y - 65, x + 50, y + 23), 180, 360, fill="#49333B")
    draw.ellipse((x - 22, y - 13, x - 15, y - 5), fill=INK)
    draw.ellipse((x + 15, y - 13, x + 22, y - 5), fill=INK)
    if expression == "surprised":
        draw.ellipse((x - 7, y + 6, x + 8, y + 24), fill="#8C4551")
    elif expression == "sleepy":
        draw.arc((x - 27, y - 15, x - 10, y - 3), 5, 175, fill=INK, width=3)
        draw.arc((x + 10, y - 15, x + 27, y - 3), 5, 175, fill=INK, width=3)
        draw.arc((x - 10, y + 4, x + 10, y + 20), 190, 350, fill=INK, width=3)
    else:
        draw.arc((x - 13, y + 3, x + 13, y + 21), 0, 180, fill=INK, width=3)


def _draw_pet(draw: ImageDraw.ImageDraw, x: int, y: int, actor: str, phase: float, expression: str) -> None:
    bob = int(math.sin(phase * math.pi * 2) * 7)
    y += bob
    # Four-legged cartoon body and a wagging tail.
    draw.ellipse((x - 76, y + 15, x + 68, y + 112), fill="#C98952" if actor == "dog" else "#E99855")
    if actor == "dog":
        draw.ellipse((x + 26, y - 38, x + 112, y + 49), fill="#C98952")
        draw.ellipse((x + 67, y - 24, x + 100, y + 29), fill="#E8B487")
        draw.ellipse((x + 76, y - 8, x + 83, y - 1), fill=INK)
        draw.ellipse((x + 105, y + 3, x + 114, y + 12), fill="#49333B")
        draw.polygon([(x + 37, y - 29), (x + 38, y - 80), (x + 72, y - 41)], fill="#9D6040")
        draw.arc((x - 110, y + 8, x - 44, y + 76), 180, 300 + int(math.sin(phase * 8) * 20), fill="#C98952", width=13)
    else:
        draw.ellipse((x + 12, y - 48, x + 106, y + 46), fill="#E99855")
        draw.polygon([(x + 21, y - 28), (x + 10, y - 95), (x + 57, y - 57)], fill="#E99855")
        draw.polygon([(x + 68, y - 54), (x + 113, y - 96), (x + 99, y - 26)], fill="#E99855")
        draw.polygon([(x + 24, y - 36), (x + 24, y - 73), (x + 46, y - 52)], fill="#ECA6A2")
        draw.ellipse((x + 47, y - 13, x + 54, y - 5), fill=INK)
        draw.ellipse((x + 81, y - 13, x + 88, y - 5), fill=INK)
        draw.polygon([(x + 65, y + 2), (x + 58, y + 10), (x + 72, y + 10)], fill="#D56B7B")
    for lx in (x - 49, x + 39):
        draw.rounded_rectangle((lx, y + 78, lx + 21, y + 137), 10, fill="#C98952")
    if actor == "dog" and expression == "happy":
        draw.ellipse((x + 74, y + 18, x + 90, y + 34), fill="#EE8A7C")


def _draw_prop(draw: ImageDraw.ImageDraw, prop: str, x: int, y: int, phase: float, scene_index: int) -> None:
    wobble = int(math.sin(phase * math.pi * 2) * 7)
    y += wobble
    # White speech-bubble backdrop anchors the visual gag.
    draw.ellipse((x - 102, y - 108, x + 102, y + 96), fill="#FFFFFF")
    draw.ellipse((x - 90, y - 96, x + 90, y + 84), fill="#F8FBFF")
    if prop in ("laptop", "phone", "camera"):
        w, h = (126, 88) if prop == "laptop" else (67, 108)
        draw.rounded_rectangle((x - w // 2, y - h // 2, x + w // 2, y + h // 2), 12, fill="#34445F")
        draw.rounded_rectangle((x - w // 2 + 8, y - h // 2 + 8, x + w // 2 - 8, y + h // 2 - 8), 6, fill="#9DD8E3")
        if prop == "laptop":
            draw.polygon([(x - 80, y + h // 2), (x + 80, y + h // 2), (x + 94, y + h // 2 + 14), (x - 94, y + h // 2 + 14)], fill="#8393A9")
            draw.ellipse((x + 17, y - 17, x + 45, y + 11), fill="#F7A79A")
            draw.text((x - 40, y + 12), "MUTED", font=_font(12, True), fill=INK)
        elif prop == "phone":
            draw.rounded_rectangle((x - 24, y - 39, x + 23, y + 40), 7, fill="#FFFFFF")
            draw.text((x - 16, y - 17), "SPOON", font=_font(9, True), fill="#536581")
        else:
            draw.ellipse((x - 15, y - 15, x + 15, y + 15), outline="#FFFFFF", width=4)
    elif prop == "fridge":
        draw.rounded_rectangle((x - 52, y - 84, x + 52, y + 89), 15, fill="#A7D7DC")
        draw.line((x - 48, y - 10, x + 48, y - 10), fill="#7CB5BD", width=4)
        draw.line((x + 30, y - 55, x + 30, y - 24), fill="#4F7980", width=6)
        draw.ellipse((x - 18, y + 8, x + 18, y + 45), fill="#F7D585")
    elif prop == "laundry":
        draw.polygon([(x - 64, y - 10), (x + 64, y - 10), (x + 48, y + 72), (x - 48, y + 72)], fill="#9B84C5")
        for i, c in enumerate(("#F17D83", "#F8D36B", "#7AC8BD")):
            draw.ellipse((x - 55 + i * 35, y - 48 - (i % 2) * 20, x - 10 + i * 35, y + 4), fill=c)
    elif prop == "leash":
        draw.arc((x - 56, y - 54, x + 56, y + 60), 195, 350, fill="#EE756F", width=11)
        draw.line((x - 4, y - 20, x + 58, y + 34), fill="#EE756F", width=8)
        draw.ellipse((x + 45, y + 22, x + 68, y + 45), fill="#F7C96A")
    elif prop == "box":
        draw.polygon([(x - 68, y - 45), (x + 15, y - 45), (x + 70, y - 10), (x - 13, y - 10)], fill="#E9B36D")
        draw.polygon([(x - 68, y - 45), (x - 13, y - 10), (x - 13, y + 67), (x - 68, y + 30)], fill="#D89A59")
        draw.polygon([(x - 13, y - 10), (x + 70, y - 10), (x + 70, y + 30), (x - 13, y + 67)], fill="#C98952")
        draw.line((x - 13, y - 10, x - 13, y + 66), fill="#F5D293", width=5)
    elif prop == "plant":
        draw.polygon([(x - 42, y + 22), (x + 42, y + 22), (x + 28, y + 78), (x - 28, y + 78)], fill="#E89072")
        draw.line((x, y + 24, x, y - 45), fill="#477D58", width=9)
        for dx, dy in [(-34, -27), (35, -51), (-35, -63), (31, -20)]:
            draw.ellipse((x + dx - 26, y + dy - 16, x + dx + 26, y + dy + 16), fill="#6DB784")
    elif prop == "mat":
        draw.rounded_rectangle((x - 72, y - 33, x + 72, y + 40), 28, fill="#8F92DC")
        draw.ellipse((x - 72, y - 33, x - 20, y + 40), fill="#C0A3E9")
    elif prop == "umbrella":
        draw.pieslice((x - 80, y - 63, x + 80, y + 72), 180, 360, fill="#E97A81")
        draw.line((x, y + 15, x, y + 87), fill="#536581", width=8)
        draw.arc((x - 7, y + 73, x + 29, y + 105), 0, 180, fill="#536581", width=7)
    else:
        draw.ellipse((x - 54, y - 49, x + 54, y + 50), fill="#F5D681")


def render_frame(scenario: dict[str, Any], scene_index: int, phase: float, seconds_per_scene: float) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    _background(image, scenario["room"], scene_index)
    draw = ImageDraw.Draw(image)
    # Brand and chapter marker
    draw.rounded_rectangle((38, 45, 318, 103), 27, fill="#FFFFFF")
    draw.ellipse((54, 60, 82, 88), fill=PALETTE[scene_index])
    draw.text((96, 60), "DAILY COMEDY STUDIO", font=_font(18, True), fill=INK)
    draw.rounded_rectangle((556, 55, 682, 98), 21, fill=INK)
    draw.text((576, 66), f"{scene_index + 1} / 4", font=_font(18, True), fill="#FFFFFF")
    # Scene art: character and symbolic prop have gentle motion.
    actor_x = 278 + int(math.sin(phase * 1.2) * 12)
    prop_x = 524
    expression = "surprised" if scene_index == 3 else ("sleepy" if "sleep" in scenario["id"] else "happy")
    if scenario["actor"] == "person":
        _draw_person(draw, actor_x, 508, phase, PALETTE[(scene_index + 1) % len(PALETTE)], expression)
    else:
        _draw_pet(draw, actor_x - 8, 636, scenario["actor"], phase, "happy")
    _draw_prop(draw, scenario["prop"], prop_x, 560, phase + scene_index * .5, scene_index)
    # Small comedy accents appear on the closing beat.
    if scene_index == 3 and phase > seconds_per_scene * .54:
        for i, (x, y) in enumerate(((167, 475), (492, 407), (597, 702), (193, 729), (437, 765), (344, 412))):
            yy = y + int(math.sin(phase * 5 + i) * 8)
            draw.polygon([(x, yy - 10), (x + 4, yy - 2), (x + 13, yy), (x + 4, yy + 4), (x, yy + 14), (x - 4, yy + 4), (x - 12, yy), (x - 4, yy - 3)], fill=PALETTE[i % 4])
    # Readable caption card designed for sound-off mobile viewing.
    draw.rounded_rectangle((34, 884, 686, 1176), 32, fill="#FFFFFF")
    draw.rounded_rectangle((58, 909, 204, 947), 17, fill=PALETTE[scene_index])
    draw.text((76, 916), "THE STORY", font=_font(15, True), fill=INK)
    caption = scenario["scenes"][scene_index]["caption"]
    font = _font(36 if len(caption) < 39 else 31, True)
    lines = _wrapped(draw, caption, font, 570)
    if len(lines) > 3:
        font = _font(27, True)
        lines = _wrapped(draw, caption, font, 570)
    line_height = 55 if font.size >= 36 else 47 if font.size >= 31 else 41
    block_height = line_height * len(lines)
    y0 = 968 + max(0, (180 - block_height) // 2)
    for i, line in enumerate(lines):
        _center_text(draw, line, y0 + i * line_height, font, INK)
    # Simple progress strip
    draw.rounded_rectangle((42, 1208, 678, 1218), 5, fill="#FFFFFF")
    progress = (scene_index + min(phase / seconds_per_scene, 1)) / 4
    draw.rounded_rectangle((42, 1208, 42 + int(636 * progress), 1218), 5, fill=PALETTE[scene_index])
    return image


def _write_audio(path: Path, seconds: float, scene_count: int) -> None:
    """Create a quiet original synthesized musical bed and soft comic chimes."""
    sample_rate = 24000
    frame_count = int(seconds * sample_rate)
    pcm = bytearray()
    # Gentle four-note plucks, a quiet sustained low tone, and scene-change chimes.
    notes = (392.0, 440.0, 523.25, 440.0, 349.23, 392.0, 466.16, 392.0)
    beat = 0.48
    for i in range(frame_count):
        t = i / sample_rate
        n = int(t / beat) % len(notes)
        local = t % beat
        envelope = math.exp(-local * 6.2) * min(1, t * 12, (seconds - t) * 8)
        pluck = math.sin(2 * math.pi * notes[n] * local) * envelope * 0.07
        bass = math.sin(2 * math.pi * 130.81 * t) * 0.018
        chime = 0.0
        for scene in range(1, scene_count):
            dt = t - scene * seconds / scene_count
            if 0 <= dt < 0.55:
                chime += math.sin(2 * math.pi * (760 - 420 * dt) * dt) * math.exp(-dt * 8) * 0.11
        value = max(-1.0, min(1.0, pluck + bass + chime))
        sample = int(value * 32767)
        pcm.extend(sample.to_bytes(2, "little", signed=True) * 2)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(sample_rate)
        out.writeframes(pcm)


def create_video(scenario: dict[str, Any], output_path: str | Path, fps: int = FPS,
                 seconds_per_scene: float = DURATION_PER_SCENE, width: int = WIDTH,
                 height: int = HEIGHT) -> Path:
    """Encode scene animation to a playable H.264/AAC MP4 with no external assets."""
    if width != WIDTH or height != HEIGHT:
        raise ValueError(f"This version renders {WIDTH}x{HEIGHT}; requested {width}x{height}")
    if fps < 1 or fps > 30 or seconds_per_scene <= 0:
        raise ValueError("fps must be 1–30 and seconds_per_scene must be positive")
    if len(scenario.get("scenes", [])) != 4:
        raise ValueError("A scenario must contain exactly four scenes")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    duration = len(scenario["scenes"]) * seconds_per_scene
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory(prefix="comedy-studio-") as temp_dir:
        audio_path = Path(temp_dir) / "original-sound.wav"
        _write_audio(audio_path, duration, len(scenario["scenes"]))
        command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-s:v", f"{width}x{height}",
                   "-r", str(fps), "-i", "-", "-i", str(audio_path),
                   "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
                   "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                   "-movflags", "+faststart", "-shortest", str(out)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            assert process.stdin is not None
            frame_total = int(round(duration * fps))
            for frame_no in range(frame_total):
                time_value = frame_no / fps
                scene_index = min(int(time_value / seconds_per_scene), 3)
                local_time = time_value - scene_index * seconds_per_scene
                frame = render_frame(scenario, scene_index, local_time, seconds_per_scene)
                process.stdin.write(frame.tobytes())
            process.stdin.close()
            stderr = process.stderr.read() if process.stderr else b""
            if process.stderr:
                process.stderr.close()
            code = process.wait(timeout=180)
        except BaseException:
            process.kill()
            process.wait()
            raise
        if code != 0:
            raise RuntimeError(f"FFmpeg video encoding failed (exit {code}): {stderr.decode(errors='replace')[-3000:]}")
    validate_video(out)
    return out


def probe_video(path: str | Path) -> dict[str, Any]:
    """Read stream details and fully decode the MP4 using bundled FFmpeg (no ffprobe needed)."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    # FFmpeg's input banner describes codecs/geometry; decoding to null also catches corrupt files.
    result = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path), "-f", "null", "-"],
                            capture_output=True, text=True, timeout=90)
    details = result.stderr
    if result.returncode:
        raise RuntimeError(f"FFmpeg could not decode the MP4: {details.strip()[-2000:]}")
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", details)
    duration = (int(duration_match.group(1)) * 3600 + int(duration_match.group(2)) * 60 +
                float(duration_match.group(3))) if duration_match else 0.0
    video_match = re.search(r"Video:\s*h264\b.*?(\d{2,5})x(\d{2,5})", details, re.S)
    audio_match = re.search(r"Audio:\s*aac\b", details)
    fps_match = re.search(r"\b(\d+(?:\.\d+)?)\s*fps", details)
    if not video_match:
        raise RuntimeError("MP4 is missing its H.264 video stream")
    width, height = int(video_match.group(1)), int(video_match.group(2))
    if (width, height) != (WIDTH, HEIGHT):
        raise RuntimeError(f"Unexpected video size: {width}x{height}")
    if not audio_match:
        raise RuntimeError("MP4 is missing its AAC audio stream")
    if duration < 1:
        raise RuntimeError("MP4 duration is missing or too short")
    return {"duration": duration, "width": width, "height": height,
            "video_codec": "h264", "audio_codec": "aac",
            "fps": f"{fps_match.group(1)} fps" if fps_match else "unknown"}


def validate_video(path: str | Path) -> dict[str, Any]:
    file = Path(path)
    if not file.is_file() or file.stat().st_size < 1000:
        raise RuntimeError(f"MP4 output is missing or too small: {file}")
    return probe_video(file)
