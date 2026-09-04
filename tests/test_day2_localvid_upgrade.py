from __future__ import annotations

from pathlib import Path

from backend.services.transcript_service import segments_to_srt
from backend.services.video_service import validate_file


def test_srt_generation_contains_timestamp_and_text():
    srt = segments_to_srt([
        {"id": 0, "start": 1.25, "end": 3.5, "text": "你好 VidInsight"}
    ])
    assert "00:00:01,250 --> 00:00:03,500" in srt
    assert "你好 VidInsight" in srt


def test_supported_extension_is_accepted():
    assert validate_file("demo.mp4") == ".mp4"


def test_unsupported_extension_is_rejected():
    try:
        validate_file("demo.txt")
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)
    else:
        raise AssertionError("TXT should be rejected")


def test_launcher_exists():
    assert Path("launcher.py").exists()
