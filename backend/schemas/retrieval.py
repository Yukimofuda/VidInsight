from __future__ import annotations

from pydantic import BaseModel, Field


class IndexResponse(BaseModel):
    video_id: str
    chunk_count: int
    collection_name: str
    chunks_path: str


class SearchHit(BaseModel):
    chunk_id: str
    text: str
    start: float
    end: float
    distance: float | None = None


class SearchResponse(BaseModel):
    video_id: str
    query: str
    top_k: int = Field(ge=1, le=20)
    hits: list[SearchHit]
