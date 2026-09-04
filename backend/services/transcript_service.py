from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
TRANSCRIPT_DIR = BASE_DIR / "storage" / "transcripts"
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)


def _task_dir(video_id: str) -> Path:
    path = TRANSCRIPT_DIR / video_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _srt_timestamp(seconds: float) -> str:
    milliseconds = max(int(round(float(seconds) * 1000)), 0)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def segments_to_srt(segments: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, segment in enumerate(segments, start=1):
        text = str(segment.get("text", "")).strip()
        if not text:
            continue
        start = _srt_timestamp(float(segment.get("start", 0)))
        end = _srt_timestamp(float(segment.get("end", 0)))
        blocks.append(f"{index}\n{start} --> {end}\n{text}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def save_transcript(video_id: str, data: dict[str, Any]) -> tuple[Path, Path]:
    directory = _task_dir(video_id)
    json_path = directory / "transcript.json"
    srt_path = directory / "transcript.srt"
    metadata_path = directory / "metadata.json"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    with srt_path.open("w", encoding="utf-8") as file:
        file.write(segments_to_srt(data.get("segments", [])))

    metadata = {
        "video_id": video_id,
        "original_name": data.get("original_name"),
        "language": data.get("language"),
        "language_probability": data.get("language_probability"),
        "duration_seconds": data.get("duration_seconds"),
        "processing_seconds": data.get("processing_seconds"),
        "asr_model": data.get("asr_model"),
    }
    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)

    return json_path, srt_path


def load_transcript(video_id: str) -> dict[str, Any] | None:
    new_path = TRANSCRIPT_DIR / video_id / "transcript.json"
    legacy_path = TRANSCRIPT_DIR / f"{video_id}.json"
    path = new_path if new_path.exists() else legacy_path
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
