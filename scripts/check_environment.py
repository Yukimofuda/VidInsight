from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VENV = (ROOT / ".venv").resolve()
EXPECTED_PYTHON = EXPECTED_VENV / "bin" / "python"


def resolved(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def main() -> int:
    errors: list[str] = []

    executable = resolved(sys.executable)
    expected_python = resolved(EXPECTED_PYTHON)

    pythonpath = os.getenv("PYTHONPATH")
    pythonhome = os.getenv("PYTHONHOME")
    no_user_site = os.getenv("PYTHONNOUSERSITE")

    contamination = [
        p
        for p in sys.path
        if "Library/Python/3.9" in str(p)
        or "/python3.9/" in str(p).lower()
    ]

    try:
        import typing_extensions

        typing_extensions_path = resolved(typing_extensions.__file__)
    except Exception as exc:
        typing_extensions_path = None
        errors.append(f"typing_extensions import failed: {exc}")

    print("VidInsight environment check")
    print()
    print(f"Python: {sys.version}")
    print(f"Executable: {executable}")
    print(f"Expected interpreter: {expected_python}")
    print(f"PYTHONPATH: {pythonpath}")
    print(f"PYTHONHOME: {pythonhome}")
    print(f"PYTHONNOUSERSITE: {no_user_site}")
    print(f"FFmpeg: {shutil.which('ffmpeg')}")
    print(f"Python 3.9 contamination: {contamination}")
    print(f"typing_extensions: {typing_extensions_path}")

    # 不用字符串比较，使用 resolve 后的真实路径。
    if executable != expected_python:
        # 某些 venv/python 可能经由符号链接指向同一解释器。
        # 同时检查 sys.prefix 是否确实位于项目 .venv。
        if resolved(sys.prefix) != EXPECTED_VENV:
            errors.append(
                "Interpreter is not project .venv/bin/python "
                f"(actual={executable})"
            )

    if contamination:
        errors.append("Python 3.9 paths are present in sys.path")

    if pythonpath:
        errors.append("PYTHONPATH should be unset")

    if pythonhome:
        errors.append("PYTHONHOME should be unset")

    if no_user_site != "1":
        errors.append("PYTHONNOUSERSITE should be 1")

    if typing_extensions_path is not None:
        expected_site = EXPECTED_VENV / "lib"
        try:
            typing_extensions_path.relative_to(expected_site)
        except ValueError:
            errors.append(
                "typing_extensions is not loaded from project .venv"
            )

    if shutil.which("ffmpeg") is None:
        errors.append("FFmpeg was not found")

    print()

    if errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK")
    print("- Project Python environment is isolated")
    print("- No Python 3.9 contamination detected")
    print("- typing_extensions is loaded from project .venv")
    print("- FFmpeg is available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
