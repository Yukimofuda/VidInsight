from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Callable

ProgressCallback = Callable[[int, str], None]


class WhisperEngine:
    """Lazy-loaded faster-whisper wrapper with optional task progress callbacks."""

    def __init__(self) -> None:
        self.model_size = os.getenv("WHISPER_MODEL", "base")
        self.device = os.getenv("WHISPER_DEVICE", "cpu")
        self.compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        self.beam_size = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
        self._model: Any | None = None

    def _load_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "faster-whisper is not installed. Run: "
                    "python -m pip install -r requirements-day2.txt"
                ) from exc
            self._model = WhisperModel(
                self.model_size, device=self.device, compute_type=self.compute_type
            )
        return self._model

    def transcribe(
        self,
        audio_path: str | Path,
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file does not exist: {audio_path}")

        started_at = time.perf_counter()
        if progress_callback:
            progress_callback(20, "正在加载 ASR 模型")
        model = self._load_model()
        segments, info = model.transcribe(
            str(audio_path), beam_size=self.beam_size, vad_filter=True
        )

        duration = float(getattr(info, "duration", 0.0) or 0.0)
        result_segments: list[dict[str, Any]] = []
        full_text: list[str] = []
        last_progress = 20

        for index, segment in enumerate(segments):
            text = segment.text.strip()
            if not text:
                continue
            end = float(segment.end)
            result_segments.append(
                {
                    "id": index,
                    "start": round(float(segment.start), 2),
                    "end": round(end, 2),
                    "text": text,
                }
            )
            full_text.append(text)
            if progress_callback and duration > 0:
                asr_progress = 20 + int(min(end / duration, 1.0) * 68)
                if asr_progress >= last_progress + 2:
                    last_progress = asr_progress
                    progress_callback(asr_progress, "正在进行语音转写")

        elapsed = round(time.perf_counter() - started_at, 3)
        language_probability = float(getattr(info, "language_probability", 0.0) or 0.0)
        if progress_callback:
            progress_callback(90, "语音转写完成，正在保存字幕")

        return {
            "language": getattr(info, "language", "unknown"),
            "language_probability": round(language_probability, 4),
            "duration_seconds": round(duration, 2),
            "processing_seconds": elapsed,
            "asr_model": self.model_size,
            "text": " ".join(full_text).strip(),
            "segments": result_segments,
        }


whisper_engine = WhisperEngine()
