from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ChunkPolicy:
    """Target window used by the segment-aware chunker.

    The policy is deliberately independent from any tokenizer/model so the
    preprocessing layer stays reusable.  A conservative character-to-token
    estimate is used until the embedding model is selected by the retrieval
    layer.
    """

    target_tokens: int
    max_tokens: int
    overlap_segments: int = 1


def target_chunk_tokens(video_minutes: float) -> tuple[int, int]:
    if video_minutes < 10:
        return (350, 500)
    if video_minutes <= 30:
        return (600, 800)
    return (900, 1200)


def policy_for_duration(duration_seconds: float) -> ChunkPolicy:
    target, maximum = target_chunk_tokens(max(duration_seconds, 0.0) / 60.0)
    return ChunkPolicy(target_tokens=target, max_tokens=maximum, overlap_segments=1)


def estimate_tokens(text: str) -> int:
    """Lightweight bilingual estimate without coupling to a model tokenizer.

    Chinese characters are close to one token each for many modern tokenizers;
    Latin text is usually several characters per token.  The estimate is only
    used for chunk sizing, not evaluation or billing.
    """

    if not text:
        return 0
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    other = max(len(text) - cjk, 0)
    return cjk + max(1, other // 4)


def _normalize_segment(segment: dict, index: int) -> dict:
    text = str(segment.get("text") or "").strip()
    return {
        "id": int(segment.get("id", index)),
        "start": float(segment.get("start", 0.0)),
        "end": float(segment.get("end", segment.get("start", 0.0))),
        "text": text,
    }


def build_chunks(
    segments: Iterable[dict],
    *,
    video_id: str,
    duration_seconds: float,
    policy: ChunkPolicy | None = None,
) -> list[dict]:
    """Build timestamp-preserving chunks from Whisper segments.

    Boundaries are always aligned to ASR segments, which means retrieval
    evidence can be mapped back to the original video without reconstructing
    timestamps later. One segment of overlap is used by default to reduce
    boundary loss while keeping duplicate context controlled.
    """

    normalized = [
        _normalize_segment(segment, index)
        for index, segment in enumerate(segments)
        if str(segment.get("text") or "").strip()
    ]
    if not normalized:
        return []

    chosen = policy or policy_for_duration(duration_seconds)
    chunks: list[dict] = []
    cursor = 0

    while cursor < len(normalized):
        start_cursor = cursor
        current: list[dict] = []
        estimated = 0

        while cursor < len(normalized):
            candidate = normalized[cursor]
            candidate_tokens = estimate_tokens(candidate["text"])
            would_exceed = current and estimated + candidate_tokens > chosen.max_tokens
            target_reached = current and estimated >= chosen.target_tokens
            if would_exceed or target_reached:
                break
            current.append(candidate)
            estimated += candidate_tokens
            cursor += 1

        # Guarantee progress even if a single segment is unusually large.
        if not current:
            current = [normalized[cursor]]
            estimated = estimate_tokens(current[0]["text"])
            cursor += 1

        text = " ".join(item["text"] for item in current).strip()
        chunk_id = f"{video_id}:chunk:{len(chunks):04d}"
        chunks.append(
            {
                "id": chunk_id,
                "video_id": video_id,
                "chunk_index": len(chunks),
                "start": current[0]["start"],
                "end": current[-1]["end"],
                "text": text,
                "estimated_tokens": estimated,
                "segment_ids": [item["id"] for item in current],
            }
        )

        if cursor >= len(normalized):
            break

        overlap = min(chosen.overlap_segments, max(len(current) - 1, 0))
        if overlap:
            cursor = max(start_cursor + 1, cursor - overlap)

    return chunks
