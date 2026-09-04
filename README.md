# VidInsight — 智影 AI 视频助手

VidInsight 是课程“进阶项目一：视频助手”的工程实现。当前 Day 2.1 已形成稳定的视频数据入口：视频/音频上传后创建后台任务，由 SQLite + Worker 调度 FFmpeg 和 faster-whisper，产出带时间戳的 JSON/SRT Transcript。Day 3 起在该 Transcript 之上构建 BGE/Chroma、BM25、Hybrid RAG、RRF 和 QA。

## Day 2.1 architecture

```text
Streamlit
   ↓ POST /api/tasks
FastAPI ─────────→ SQLite video_tasks
                       ↓
                    Worker
                       ↓
                    FFmpeg
                       ↓
                faster-whisper
                       ↓
        transcript.json + transcript.srt
                       ↓
                 status=completed
                       ↓
Streamlit ← GET status/transcript
```

## Run on macOS

```bash
bash scripts/setup_day2.sh
bash scripts/run_all.sh
```

Or:

```bash
source .venv/bin/activate
export PYTHONNOUSERSITE=1
python launcher.py
```

- UI: http://127.0.0.1:8501
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## API

- `POST /api/tasks` — upload media and create background task (202)
- `GET /api/tasks/{task_id}` — progress/status
- `GET /api/tasks` — recent tasks
- `GET /api/videos/{video_id}/transcript` — completed transcript
- `POST /api/videos/process` — legacy synchronous compatibility endpoint

## Day 2 scope

Implemented: upload, format validation, SQLite task state, background worker, FFmpeg 16k mono WAV, faster-whisper, language detection, timestamps, JSON/SRT/metadata persistence, progress UI, launcher.

Deferred: platform download/cookies, vocal separation, LLM summary, vector/RAG stack.

## Open-source references

The team studies `P47Parzival/Video-RAG` for the later RAG layer and `sunglasses233/LocalVid-Summarizer` for local-video engineering patterns. See `THIRD_PARTY_NOTICES.md`. VidInsight's Day 2.1 code is independently implemented around the existing project structure.

## 2026-09-04 architecture update

The ingestion and retrieval lifecycles are intentionally separated:

```text
Upload -> SQLite Task -> Worker -> FFmpeg -> ASR -> Transcript(JSON/SRT)
Transcript -> Adaptive Chunk -> BGE/Chroma -> timestamped semantic evidence
```

The retrieval stack is lazy-loaded. A failed embedding model download must not prevent video upload or ASR from completing.

### macOS environment isolation

Do not add historical Python user-site folders to global `PYTHONPATH`. VidInsight launch scripts unset `PYTHONPATH`/`PYTHONHOME`, set `PYTHONNOUSERSITE=1`, and execute `.venv/bin/python` explicitly.

Run:

```bash
./.venv/bin/python scripts/check_environment.py
```

before starting services.
