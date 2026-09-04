#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

unset PYTHONPATH || true
unset PYTHONHOME || true
export PYTHONNOUSERSITE=1

if [[ "$(uname -s)" == "Darwin" ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    echo "[ERROR] Homebrew not found. Install Homebrew first: https://brew.sh"
    exit 1
  fi
  if ! command -v python3.11 >/dev/null 2>&1 && [[ ! -x "$(brew --prefix python@3.11 2>/dev/null)/bin/python3.11" ]]; then
    echo "[INFO] Installing Python 3.11..."
    brew install python@3.11
  fi
  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[INFO] Installing FFmpeg..."
    brew install ffmpeg
  fi
  PY311="$(brew --prefix python@3.11)/bin/python3.11"
else
  PY311="$(command -v python3.11 || true)"
  if [[ -z "$PY311" ]]; then
    echo "[ERROR] Python 3.11 is required."
    exit 1
  fi
  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[ERROR] FFmpeg is required. Install it with your package manager."
    exit 1
  fi
fi

RECREATE=0
if [[ ! -x .venv/bin/python ]]; then
  RECREATE=1
else
  CURRENT="$(.venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
  [[ "$CURRENT" == "3.11" ]] || RECREATE=1
fi

if [[ "$RECREATE" == "1" ]]; then
  echo "[INFO] Creating clean Python 3.11 virtual environment..."
  rm -rf .venv
  "$PY311" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-day2.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[INFO] Created .env from .env.example"
fi

mkdir -p storage/videos storage/audio storage/transcripts storage/sqlite storage/chroma

echo "[INFO] Environment checks"
python --version
python -c 'import sys; print(sys.executable)'
python -c 'import fastapi, anyio, typing_extensions, sqlite3; print("FastAPI/AnyIO/SQLite OK"); print(typing_extensions.__file__)'
ffmpeg -version | head -n 1
python -m pytest -q tests/test_day1.py tests/test_day2.py tests/test_day2_localvid_upgrade.py tests/test_task_db.py

echo
echo "[DONE] Day 2.1 environment is ready."
echo "Recommended: source .venv/bin/activate && export PYTHONNOUSERSITE=1 && python launcher.py"
echo "Or separate terminals:"
echo "  API:    bash scripts/run_backend.sh"
echo "  Worker: bash scripts/run_worker.sh"
echo "  UI:     bash scripts/run_frontend.sh"
