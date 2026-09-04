from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parents[2]
VIDEO_DIR = BASE_DIR / "storage" / "videos"
AUDIO_DIR = BASE_DIR / "storage" / "audio"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".avi", ".webm", ".mp3", ".wav", ".m4a",
}


def validate_file(filename: str) -> str:
    if not filename:
        raise ValueError("Filename is empty.")
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported file type: {extension or '(none)'}. Allowed: {allowed}")
    return extension


def save_upload(file: UploadFile, video_id: str | None = None) -> tuple[str, Path]:
    extension = validate_file(file.filename or "")
    video_id = video_id or uuid.uuid4().hex
    destination = VIDEO_DIR / f"{video_id}{extension}"
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    if destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ValueError("Uploaded file is empty.")
    return video_id, destination


def extract_audio(video_path: Path, video_id: str) -> Path:
    output_path = AUDIO_DIR / f"{video_id}.wav"
    command = [
        "ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", str(output_path),
    ]
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )
    except FileNotFoundError as exc:
        raise RuntimeError("FFmpeg is not installed or not available in PATH.") from exc
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{result.stderr[-4000:]}")
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("FFmpeg completed but no audio file was produced.")
    return output_path
