# VidInsight - RAG V1 starter (prepared on 2026-09-04)

## Why this is the next task

Day 2 freezes the ingestion boundary at a timestamped transcript. The next layer consumes that artifact instead of reaching back into FFmpeg/Whisper. This keeps ASR and retrieval independently testable and replaceable.

## Implemented starter

1. Segment-aware adaptive chunking.
2. Timestamp preservation from ASR segment -> chunk.
3. `storage/chunks/<video_id>/chunks.json` persistence.
4. Lazy-loaded SentenceTransformer adapter.
5. Per-video persistent Chroma collection.
6. `POST /api/videos/{video_id}/index`.
7. `GET /api/videos/{video_id}/search?q=...&top_k=5`.

## Explicit boundary

- `backend/services/index_service.py` orchestrates retrieval preparation.
- `ai/preprocessing/chunker.py` knows nothing about Chroma/FastAPI.
- `ai/retrieval/vector_store.py` knows nothing about UploadFile/FFmpeg/Whisper.
- Day 2 worker does **not** automatically index a video yet. ASR completion therefore remains valid even if the embedding model is unavailable.

## Next iteration

After semantic retrieval is validated on the Mac:

- add BM25 sparse retriever;
- normalize result schema;
- fuse dense + sparse rankings through RRF;
- then add LLM grounded QA over the fused top-K evidence.
