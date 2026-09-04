from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    id: int
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    text: str


class VideoProcessResponse(BaseModel):
    video_id: str
    original_name: str
    language: str
    language_probability: float
    duration_seconds: float
    processing_seconds: float
    asr_model: str
    text: str
    segments: list[TranscriptSegment]
