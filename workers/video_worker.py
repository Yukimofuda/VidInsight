from __future__ import annotations

import os
import signal
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("PYTHONNOUSERSITE", "1")

from ai.asr.whisper_engine import whisper_engine
from backend.services.task_db import claim_next_pending_task, init_db, update_task
from backend.services.transcript_service import save_transcript
from backend.services.video_service import extract_audio

POLL_SECONDS = float(os.getenv("VIDINSIGHT_WORKER_POLL_SECONDS", "1.5"))
_RUNNING = True


def _stop(*_args):
    global _RUNNING
    _RUNNING = False


def process_task(task: dict) -> None:
    task_id = task["id"]
    video_path = Path(task["source_path"])
    try:
        update_task(task_id, status="extracting_audio", progress=8, stage_message="FFmpeg 正在提取 16kHz 单声道音频")
        audio_path = extract_audio(video_path, task_id)
        update_task(task_id, status="transcribing", progress=18, stage_message="音频提取完成，准备 Whisper")

        def report(progress: int, message: str) -> None:
            update_task(
                task_id,
                status="transcribing" if progress < 90 else "writing_transcript",
                progress=progress,
                stage_message=message,
            )

        transcript = whisper_engine.transcribe(audio_path, progress_callback=report)
        result = {
            "video_id": task_id,
            "original_name": task["original_name"],
            **transcript,
        }
        json_path, srt_path = save_transcript(task_id, result)
        update_task(
            task_id,
            status="completed",
            progress=100,
            stage_message="转写完成",
            language=transcript["language"],
            duration_seconds=transcript["duration_seconds"],
            processing_seconds=transcript["processing_seconds"],
            asr_model=transcript["asr_model"],
            transcript_json=str(json_path),
            transcript_srt=str(srt_path),
            error_message=None,
        )
        print(f"[VidInsight Worker] completed {task_id} - {task['original_name']}", flush=True)
    except Exception as exc:
        update_task(
            task_id,
            status="failed",
            stage_message="处理失败",
            error_message=str(exc),
        )
        print(f"[VidInsight Worker] failed {task_id}: {exc}", flush=True)


def run_worker_loop() -> None:
    init_db()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    print("[VidInsight Worker] started; waiting for pending tasks...", flush=True)
    while _RUNNING:
        task = claim_next_pending_task()
        if task:
            process_task(task)
            continue
        time.sleep(POLL_SECONDS)
    print("[VidInsight Worker] stopped", flush=True)


if __name__ == "__main__":
    run_worker_loop()
