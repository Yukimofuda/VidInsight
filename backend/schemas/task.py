from __future__ import annotations

from pydantic import BaseModel, Field


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    original_name: str


class TaskStatusResponse(BaseModel):
    task_id: str
    original_name: str
    status: str
    progress: int = Field(ge=0, le=100)
    stage_message: str
    language: str | None = None
    duration_seconds: float | None = None
    processing_seconds: float | None = None
    asr_model: str | None = None
    transcript_json: str | None = None
    transcript_srt: str | None = None
    error_message: str | None = None
    created_at: str
    updated_at: str
