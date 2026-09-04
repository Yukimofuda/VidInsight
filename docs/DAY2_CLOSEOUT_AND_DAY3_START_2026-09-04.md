# Day 2 closeout + Day 3 starter

## Day 2 closeout gate

Before marking the ingestion layer fully accepted on the member Mac, retain evidence for:

1. `GET /health` returns 200.
2. A real 30s–2min MP4 is submitted through `POST /api/tasks`.
3. Task reaches `completed` through the worker.
4. `storage/audio/<id>.wav` is PCM 16 kHz mono.
5. Transcript JSON/SRT/metadata exist and timestamp segments are non-empty.
6. Streamlit at `127.0.0.1:8501` displays progress and transcript.
7. `./.venv/bin/python scripts/check_environment.py` reports no Python 3.9 contamination.

## Next task: RAG V1 dense baseline

Implemented as a starter on 9/4 so 9/5 can focus on validation rather than restructuring:

- `ai/preprocessing/chunker.py`: segment-aware adaptive chunking;
- `ai/retrieval/vector_store.py`: lazy SentenceTransformer + Chroma adapter;
- `backend/services/index_service.py`: orchestration and chunks persistence;
- `POST /api/videos/{video_id}/index`;
- `GET /api/videos/{video_id}/search`;
- `app/pages/workspace.py`: index/search validation UI.

Do not add BM25/RRF/LLM until dense retrieval is verified with real video evidence. This limits failure variables and keeps module boundaries stable.

## Automated checks in the prepared package

`pytest -q` => **16 passed** in the package-generation environment. Heavy model inference was intentionally not claimed as passed and must be validated on the member Mac.
