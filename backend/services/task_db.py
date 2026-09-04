from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "storage" / "sqlite" / "vidinsight.db"
_LOCK = threading.Lock()


def _db_path() -> Path:
    configured = os.getenv("VIDINSIGHT_DB_PATH")
    path = Path(configured).expanduser().resolve() if configured else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_db_path(), timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS video_tasks (
                id TEXT PRIMARY KEY,
                original_name TEXT NOT NULL,
                source_path TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                stage_message TEXT NOT NULL DEFAULT '',
                language TEXT,
                duration_seconds REAL,
                processing_seconds REAL,
                asr_model TEXT,
                transcript_json TEXT,
                transcript_srt TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_video_tasks_status_created "
            "ON video_tasks(status, created_at)"
        )


def create_task(task_id: str, original_name: str, source_path: str) -> dict[str, Any]:
    init_db()
    now = _now()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO video_tasks (
                id, original_name, source_path, status, progress,
                stage_message, created_at, updated_at
            ) VALUES (?, ?, ?, 'pending', 0, '等待后台处理', ?, ?)
            """,
            (task_id, original_name, source_path, now, now),
        )
    return get_task(task_id) or {}


def get_task(task_id: str) -> dict[str, Any] | None:
    init_db()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM video_tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None


def list_tasks(limit: int = 50) -> list[dict[str, Any]]:
    init_db()
    limit = min(max(int(limit), 1), 200)
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM video_tasks ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def update_task(task_id: str, **fields: Any) -> None:
    if not fields:
        return
    allowed = {
        "status", "progress", "stage_message", "language", "duration_seconds",
        "processing_seconds", "asr_model", "transcript_json", "transcript_srt",
        "error_message",
    }
    safe = {key: value for key, value in fields.items() if key in allowed}
    if not safe:
        return
    safe["updated_at"] = _now()
    assignments = ", ".join(f"{key} = ?" for key in safe)
    values = list(safe.values()) + [task_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE video_tasks SET {assignments} WHERE id = ?", values)


def claim_next_pending_task() -> dict[str, Any] | None:
    """Atomically claim one pending task. One worker is enough for Day 2."""
    init_db()
    with _LOCK:
        conn = sqlite3.connect(_db_path(), timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM video_tasks WHERE status = 'pending' "
                "ORDER BY created_at ASC LIMIT 1"
            ).fetchone()
            if row is None:
                conn.commit()
                return None
            now = _now()
            conn.execute(
                "UPDATE video_tasks SET status = 'extracting_audio', progress = 5, "
                "stage_message = '正在提取音频', updated_at = ? WHERE id = ? AND status = 'pending'",
                (now, row["id"]),
            )
            conn.commit()
            claimed = conn.execute(
                "SELECT * FROM video_tasks WHERE id = ?", (row["id"],)
            ).fetchone()
            return dict(claimed) if claimed else None
        finally:
            conn.close()
