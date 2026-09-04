from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VENV = PROJECT_ROOT / ".venv"

print("VidInsight environment check")
print("Python:", sys.version.replace("\n", " "))
print("Executable:", sys.executable)
print("PYTHONPATH:", os.getenv("PYTHONPATH"))
print("PYTHONHOME:", os.getenv("PYTHONHOME"))
print("PYTHONNOUSERSITE:", os.getenv("PYTHONNOUSERSITE"))
print("FFmpeg:", shutil.which("ffmpeg") or "NOT FOUND")

contamination = [item for item in sys.path if "Library/Python/3.9" in item or "Python/3.9" in item]
print("Python 3.9 contamination:", contamination)

errors: list[str] = []
if not str(Path(sys.executable).resolve()).startswith(str(EXPECTED_VENV.resolve())):
    errors.append("Interpreter is not project .venv/bin/python")
if contamination:
    errors.append("Python 3.9 user-site leaked into sys.path")
if os.getenv("PYTHONPATH"):
    errors.append("PYTHONPATH should be unset for this project")
if not shutil.which("ffmpeg"):
    errors.append("FFmpeg is not available")

try:
    import typing_extensions
    print("typing_extensions:", typing_extensions.__file__)
    if "Python/3.9" in str(typing_extensions.__file__):
        errors.append("typing_extensions loaded from Python 3.9")
except Exception as exc:
    errors.append(f"typing_extensions import failed: {exc}")

if errors:
    print("\nFAILED")
    for item in errors:
        print("-", item)
    raise SystemExit(1)

print("\nEnvironment isolation OK")
