#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
unset PYTHONPATH || true
unset PYTHONHOME || true
export PYTHONNOUSERSITE=1
PYTHON="$ROOT/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  echo "ERROR: missing project interpreter: $PYTHON" >&2
  exit 1
fi
exec "$PYTHON" -m workers.video_worker
