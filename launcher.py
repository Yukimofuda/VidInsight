from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def command(*parts: str) -> list[str]:
    return [sys.executable, *parts]


def main() -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    processes = [
        ("API", command("-m", "uvicorn", "backend.api.main:app", "--reload", "--port", "8000")),
        ("Worker", command("-m", "workers.video_worker")),
        ("UI", command("-m", "streamlit", "run", "app/main.py", "--server.address", "127.0.0.1", "--server.port", "8501", "--server.headless", "true")),
    ]
    running: list[tuple[str, subprocess.Popen]] = []
    try:
        for name, cmd in processes:
            print(f"[Launcher] starting {name}: {' '.join(cmd)}")
            proc = subprocess.Popen(cmd, cwd=ROOT, env=env)
            running.append((name, proc))
            time.sleep(0.8)
        print("\nVidInsight is starting:")
        print("  API docs: http://127.0.0.1:8000/docs")
        print("  Health:   http://127.0.0.1:8000/health")
        print("  UI:       http://127.0.0.1:8501")
        print("Press Ctrl+C to stop all services.\n")
        while True:
            for name, proc in running:
                code = proc.poll()
                if code is not None:
                    raise RuntimeError(f"{name} exited with code {code}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Launcher] stopping services...")
    finally:
        for _, proc in running:
            if proc.poll() is None:
                proc.send_signal(signal.SIGINT)
        deadline = time.time() + 6
        for _, proc in running:
            timeout = max(deadline - time.time(), 0.1)
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.terminate()


if __name__ == "__main__":
    main()
