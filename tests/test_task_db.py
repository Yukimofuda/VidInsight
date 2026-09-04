from __future__ import annotations


def test_task_lifecycle(tmp_path, monkeypatch):
    import backend.services.task_db as db

    db_path = tmp_path / "vidinsight.db"
    monkeypatch.setattr(db, "_db_path", lambda: db_path)
    db.init_db()
    created = db.create_task("task-1", "demo.mp4", "/tmp/demo.mp4")
    assert created["status"] == "pending"
    claimed = db.claim_next_pending_task()
    assert claimed is not None
    assert claimed["id"] == "task-1"
    assert claimed["status"] == "extracting_audio"
    db.update_task("task-1", status="completed", progress=100, stage_message="done")
    final = db.get_task("task-1")
    assert final is not None
    assert final["status"] == "completed"
    assert final["progress"] == 100
