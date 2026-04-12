#!/usr/bin/env python3
"""Empaqueta release del ejecutable economy-toolkit.

Flujo:
1) Compila binario one-file (PyInstaller) usando build_economy_toolkit_executable.py.
2) Genera zip con nombre por plataforma.
3) Escribe checksums SHA256.
4) Opcional: firma el checksum con GPG (detached signature).

Variables opcionales:
- ECONOMY_GPG_KEY_ID: key id para firmar checksum (.asc)
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"
RELEASE_DIR = DIST_DIR / "release"
BUILD_SCRIPT = REPO_ROOT / "tools" / "build_economy_toolkit_executable.py"


def detect_binary_name() -> str:
    return "economy-toolkit.exe" if sys.platform.startswith("win") else "economy-toolkit"


def platform_id() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower().replace(" ", "_")
    py = f"py{sys.version_info.major}{sys.version_info.minor}"
    return f"{system}-{machine}-{py}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def maybe_sign_checksum(checksum_file: Path) -> None:
    key_id = os.getenv("ECONOMY_GPG_KEY_ID", "").strip()
    gpg = shutil.which("gpg")
    if not key_id:
        print("[info] ECONOMY_GPG_KEY_ID no definido; se omite firma GPG.")
        return
    if not gpg:
        print("[warn] gpg no encontrado; no se pudo firmar checksum.")
        return

    sig_file = checksum_file.with_suffix(checksum_file.suffix + ".asc")
    cmd = [
        gpg,
        "--batch",
        "--yes",
        "--armor",
        "--local-user",
        key_id,
        "--output",
        str(sig_file),
        "--detach-sign",
        str(checksum_file),
    ]
    print("[run]", " ".join(cmd))
    rc = subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode
    if rc == 0 and sig_file.exists():
        print(f"[ok] firma checksum: {sig_file}")
    else:
        print("[warn] fallo firma GPG de checksum.")


def main() -> int:
    cmd = [sys.executable, str(BUILD_SCRIPT)]
    print("[run]", " ".join(cmd))
    rc = subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode
    if rc != 0:
        return int(rc)

    bin_name = detect_binary_name()
    binary_path = DIST_DIR / bin_name
    if not binary_path.exists():
        print(f"[error] no se encontró binario esperado: {binary_path}")
        return 3

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    package_name = f"economy-toolkit-{platform_id()}.zip"
    package_path = RELEASE_DIR / package_name

    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(binary_path, arcname=bin_name)

    checksum = sha256_file(package_path)
    checksum_file = RELEASE_DIR / f"{package_name}.sha256"
    checksum_file.write_text(f"{checksum}  {package_name}\n", encoding="utf-8")

    maybe_sign_checksum(checksum_file)

    print(f"[ok] package: {package_path}")
    print(f"[ok] sha256:  {checksum_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
