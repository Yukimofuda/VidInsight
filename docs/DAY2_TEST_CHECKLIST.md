# Day 2.1 Test Checklist

| ID | Test | Expected |
|---|---|---|
| T01 | GET /health | 200, `pipeline=sqlite-worker-asr` |
| T02 | POST /api/tasks with MP4 | 202 + task_id |
| T03 | Worker claims pending task | status changes to extracting_audio/transcribing |
| T04 | FFmpeg output | pcm_s16le, 16000 Hz, mono |
| T05 | Chinese speech | language=zh and transcript non-empty |
| T06 | Segment timestamps | every segment start <= end |
| T07 | Transcript persistence | JSON + SRT + metadata exist |
| T08 | Task progress | eventually completed=100 |
| T09 | TXT upload | HTTP 400 |
| T10 | Streamlit | progress + final transcript visible |
| T11 | Restart API | completed task remains in SQLite |
| T12 | Git hygiene | no .env/media/transcript/db staged |
