from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "storage" / "chroma"
DEFAULT_EMBEDDING_MODEL = os.getenv("VIDINSIGHT_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")


class VectorStore:
    """Thin adapter around Chroma and sentence-transformers.

    Heavy dependencies are imported lazily so ingestion/ASR can run without
    loading the embedding stack. This keeps subsystem boundaries explicit and
    avoids making video upload depend on RAG availability.
    """

    def __init__(self, persist_dir: Path | None = None, model_name: str | None = None):
        self.persist_dir = persist_dir or CHROMA_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name or DEFAULT_EMBEDDING_MODEL
        self._client = None
        self._model = None

    @property
    def client(self):
        if self._client is None:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        return self._client

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    @staticmethod
    def collection_name(video_id: str) -> str:
        # Chroma collection names must remain portable and predictable.
        return f"video_{video_id[:24]}"

    def _encode(self, texts: Iterable[str]) -> list[list[float]]:
        values = list(texts)
        embeddings = self.model.encode(values, normalize_embeddings=True)
        return [row.tolist() for row in embeddings]

    def index_chunks(self, video_id: str, chunks: list[dict]) -> str:
        name = self.collection_name(video_id)
        collection = self.client.get_or_create_collection(
            name=name,
            metadata={"video_id": video_id, "embedding_model": self.model_name},
        )
        if not chunks:
            return name

        ids = [item["id"] for item in chunks]
        documents = [item["text"] for item in chunks]
        metadatas = [
            {
                "video_id": video_id,
                "chunk_index": item["chunk_index"],
                "start": item["start"],
                "end": item["end"],
                "estimated_tokens": item["estimated_tokens"],
            }
            for item in chunks
        ]
        embeddings = self._encode(documents)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return name

    def search(self, video_id: str, query: str, top_k: int = 5) -> list[dict]:
        name = self.collection_name(video_id)
        collection = self.client.get_collection(name=name)
        query_embedding = self._encode([query])[0]
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=max(1, min(int(top_k), 20)),
            include=["documents", "metadatas", "distances"],
        )
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        hits: list[dict] = []
        for idx, chunk_id in enumerate(ids):
            metadata = metadatas[idx] or {}
            hits.append(
                {
                    "chunk_id": chunk_id,
                    "text": documents[idx] or "",
                    "start": float(metadata.get("start", 0.0)),
                    "end": float(metadata.get("end", 0.0)),
                    "distance": float(distances[idx]) if idx < len(distances) else None,
                }
            )
        return hits


vector_store = VectorStore()
