from __future__ import annotations

import json
from pathlib import Path

from ai.preprocessing.chunker import build_chunks
from ai.retrieval.vector_store import vector_store
from backend.services.transcript_service import load_transcript

BASE_DIR = Path(__file__).resolve().parents[2]
CHUNK_DIR = BASE_DIR / "storage" / "chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)


def chunks_path(video_id: str) -> Path:
    return CHUNK_DIR / video_id / "chunks.json"


def build_and_save_chunks(video_id: str) -> tuple[list[dict], Path]:
    transcript = load_transcript(video_id)
    if transcript is None:
        raise FileNotFoundError("Transcript not found. Complete ASR before indexing.")

    chunks = build_chunks(
        transcript.get("segments", []),
        video_id=video_id,
        duration_seconds=float(transcript.get("duration_seconds") or 0.0),
    )
    path = chunks_path(video_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "video_id": video_id,
                "duration_seconds": transcript.get("duration_seconds"),
                "chunk_count": len(chunks),
                "chunks": chunks,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return chunks, path


def index_video(video_id: str) -> dict:
    chunks, path = build_and_save_chunks(video_id)
    collection = vector_store.index_chunks(video_id, chunks)
    return {
        "video_id": video_id,
        "chunk_count": len(chunks),
        "collection_name": collection,
        "chunks_path": str(path),
    }


def search_video(video_id: str, query: str, top_k: int = 5) -> dict:
    query = query.strip()
    if not query:
        raise ValueError("Query cannot be empty.")
    return {
        "video_id": video_id,
        "query": query,
        "top_k": max(1, min(int(top_k), 20)),
        "hits": vector_store.search(video_id, query, top_k=top_k),
    }
