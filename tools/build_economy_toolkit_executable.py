#!/usr/bin/env python3
"""Build helper para generar ejecutable del Economy Toolkit.

Uso:
  python tools/build_economy_toolkit_executable.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = REPO_ROOT / "tools" / "economy_toolkit.py"
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"


def main() -> int:
    if not TOOLKIT.exists():
        print(f"[error] no existe toolkit: {TOOLKIT}")
        return 1

    pyinstaller = shutil.which("pyinstaller")
    if not pyinstaller:
        print("[error] PyInstaller no está instalado. Ejecutá: python -m pip install pyinstaller")
        return 2

    cmd = [
        pyinstaller,
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "economy-toolkit",
        str(TOOLKIT),
    ]
    print("[run]", " ".join(cmd))
    rc = subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode
    if rc != 0:
        return int(rc)

    exe = DIST_DIR / ("economy-toolkit.exe" if sys.platform.startswith("win") else "economy-toolkit")
    if exe.exists():
        print(f"[ok] ejecutable generado: {exe}")
    else:
        print("[warn] build finalizó pero no se encontró el binario esperado en dist/.")

    print(f"[info] build dir: {BUILD_DIR}")
    print(f"[info] dist dir:  {DIST_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
