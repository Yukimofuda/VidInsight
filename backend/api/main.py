from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile

load_dotenv()

from ai.asr.whisper_engine import whisper_engine
from backend.schemas.task import TaskCreateResponse, TaskStatusResponse
from backend.schemas.video import VideoProcessResponse
from backend.schemas.retrieval import IndexResponse, SearchResponse
from backend.services.task_db import create_task, get_task, init_db, list_tasks
from backend.services.transcript_service import load_transcript, save_transcript
from backend.services.video_service import extract_audio, save_upload
from backend.services.index_service import index_video, search_video

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="VidInsight API",
    description=(
        "Day 2 video ingestion pipeline: upload -> SQLite task -> worker -> FFmpeg -> "
        "faster-whisper -> JSON/SRT transcript. Inspired by LocalVid-Summarizer's "
        "task/worker separation, implemented independently for VidInsight."
    ),
    version="0.3.0-dev",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "project": "VidInsight",
        "day": "2026-09-04",
        "pipeline": "sqlite-worker-asr",
    }


@app.post("/api/tasks", response_model=TaskCreateResponse, status_code=202)
def create_video_task(file: UploadFile = File(...)):
    try:
        task_id = uuid.uuid4().hex
        _, video_path = save_upload(file, video_id=task_id)
        task = create_task(task_id, file.filename or video_path.name, str(video_path))
        return {
            "task_id": task_id,
            "status": task["status"],
            "progress": task["progress"],
            "original_name": task["original_name"],
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


def _task_response(task: dict) -> dict:
    return {
        "task_id": task["id"],
        "original_name": task["original_name"],
        "status": task["status"],
        "progress": task["progress"],
        "stage_message": task["stage_message"],
        "language": task["language"],
        "duration_seconds": task["duration_seconds"],
        "processing_seconds": task["processing_seconds"],
        "asr_model": task["asr_model"],
        "transcript_json": task["transcript_json"],
        "transcript_srt": task["transcript_srt"],
        "error_message": task["error_message"],
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
    }


@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
def get_video_task(task_id: str):
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return _task_response(task)


@app.get("/api/tasks")
def get_recent_tasks(limit: int = 20):
    return [_task_response(task) for task in list_tasks(limit=limit)]


@app.get("/api/videos/{video_id}/transcript", response_model=VideoProcessResponse)
def get_transcript(video_id: str):
    transcript = load_transcript(video_id)
    if transcript is None:
        raise HTTPException(status_code=404, detail="Transcript not found.")
    return transcript


@app.post("/api/videos/process", response_model=VideoProcessResponse)
def process_video_compatibility(file: UploadFile = File(...)):
    """Compatibility endpoint from the first Day 2 build; synchronous and not used by the UI."""
    try:
        video_id, video_path = save_upload(file)
        audio_path = extract_audio(video_path, video_id)
        transcript = whisper_engine.transcribe(audio_path)
        result = {
            "video_id": video_id,
            "original_name": file.filename or Path(video_path).name,
            **transcript,
        }
        save_transcript(video_id, result)
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/api/videos/{video_id}/index", response_model=IndexResponse)
def create_video_index(video_id: str):
    """Day 3 starter: build timestamp-preserving chunks and a per-video Chroma index."""
    try:
        return index_video(video_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/api/videos/{video_id}/search", response_model=SearchResponse)
def semantic_search(video_id: str, q: str, top_k: int = 5):
    """Day 3 starter: semantic retrieval only. Hybrid BM25/RRF is the next iteration."""
    try:
        return search_video(video_id, q, top_k=top_k)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        message = str(error)
        if "does not exist" in message.lower() or "not found" in message.lower():
            raise HTTPException(status_code=404, detail="Video index not found. Create the index first.") from error
        raise HTTPException(status_code=500, detail=message) from error
