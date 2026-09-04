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
exec "$PYTHON" -m streamlit run app/main.py \
  --server.address 127.0.0.1 \
  --server.port 8501 \
  --server.headless true
