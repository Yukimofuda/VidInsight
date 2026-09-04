from pathlib import Path

import pytest

from backend.services.transcript_service import load_transcript, save_transcript
from backend.services.video_service import validate_file


def test_supported_video_extensions():
    for filename in ["demo.mp4", "clip.MOV", "audio.mp3", "voice.wav"]:
        assert validate_file(filename).startswith(".")


def test_reject_unsupported_extension():
    with pytest.raises(ValueError):
        validate_file("notes.txt")


def test_reject_empty_filename():
    with pytest.raises(ValueError):
        validate_file("")


def test_transcript_roundtrip_json_and_srt(tmp_path, monkeypatch):
    import backend.services.transcript_service as service

    monkeypatch.setattr(service, "TRANSCRIPT_DIR", tmp_path)
    payload = {
        "video_id": "abc123",
        "original_name": "demo.mp4",
        "language": "zh",
        "language_probability": 0.99,
        "duration_seconds": 2.0,
        "processing_seconds": 0.3,
        "asr_model": "base",
        "text": "你好",
        "segments": [{"id": 0, "start": 0.0, "end": 2.0, "text": "你好"}],
    }
    json_path, srt_path = save_transcript("abc123", payload)
    assert json_path == Path(tmp_path) / "abc123" / "transcript.json"
    assert srt_path == Path(tmp_path) / "abc123" / "transcript.srt"
    assert srt_path.exists()
    assert "00:00:00,000 --> 00:00:02,000" in srt_path.read_text(encoding="utf-8")
    assert load_transcript("abc123") == payload
