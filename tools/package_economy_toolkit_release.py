#!/usr/bin/env python3
"""Empaqueta release del ejecutable economy-toolkit.

Flujo:
1) Compila binario one-file (PyInstaller) usando build_economy_toolkit_executable.py.
2) (Fase 1) firma binario por plataforma cuando hay credenciales.
3) Genera zip con nombre por plataforma.
4) Escribe checksum SHA256 del zip.
5) Firma opcional del checksum con GPG.

Variables opcionales:
- WINDOWS_SIGN_PFX_BASE64 / WINDOWS_SIGN_PFX_PASSWORD: firma Authenticode en Windows.
- MACOS_SIGN_IDENTITY: firma codesign en macOS.
- ECONOMY_GPG_KEY_ID: firma detached .asc de checksum (y binario en Linux).
"""

from __future__ import annotations

import base64
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
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


def sign_with_gpg(target_file: Path) -> None:
    key_id = os.getenv("ECONOMY_GPG_KEY_ID", "").strip()
    gpg = shutil.which("gpg")
    if not key_id or not gpg:
        return

    sig_file = target_file.with_suffix(target_file.suffix + ".asc")
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
        str(target_file),
    ]
    print("[run]", " ".join(cmd))
    rc = subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode
    if rc == 0 and sig_file.exists():
        print(f"[ok] firma GPG: {sig_file}")
    else:
        print(f"[warn] fallo firma GPG: {target_file.name}")


def maybe_sign_binary(binary_path: Path) -> None:
    system = platform.system().lower()

    if system == "windows":
        pfx_b64 = os.getenv("WINDOWS_SIGN_PFX_BASE64", "").strip()
        pfx_pass = os.getenv("WINDOWS_SIGN_PFX_PASSWORD", "").strip()
        signtool = shutil.which("signtool")
        if not (pfx_b64 and pfx_pass and signtool):
            print("[info] firma Windows omitida (faltan secret/signtool).")
            return

        with tempfile.TemporaryDirectory() as td:
            pfx_path = Path(td) / "codesign.pfx"
            pfx_path.write_bytes(base64.b64decode(pfx_b64))
            cmd = [
                signtool,
                "sign",
                "/f",
                str(pfx_path),
                "/p",
                pfx_pass,
                "/fd",
                "SHA256",
                "/tr",
                "http://timestamp.digicert.com",
                "/td",
                "SHA256",
                str(binary_path),
            ]
            print("[run]", " ".join(cmd[:-2] + ["***", "***"]))
            rc = subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode
            if rc == 0:
                print(f"[ok] firmado Windows: {binary_path.name}")
            else:
                print("[warn] falló firma Windows.")
        return

    if system == "darwin":
        identity = os.getenv("MACOS_SIGN_IDENTITY", "").strip()
        codesign = shutil.which("codesign")
        if not (identity and codesign):
            print("[info] firma macOS omitida (falta identity/codesign).")
            return

        cmd = [codesign, "--force", "--timestamp", "--sign", identity, str(binary_path)]
        print("[run]", " ".join(cmd))
        rc = subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode
        if rc == 0:
            print(f"[ok] firmado macOS: {binary_path.name}")
        else:
            print("[warn] falló firma macOS.")
        return

    # Linux: firma detached opcional con GPG del binario
    sign_with_gpg(binary_path)


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

    maybe_sign_binary(binary_path)

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    package_name = f"economy-toolkit-{platform_id()}.zip"
    package_path = RELEASE_DIR / package_name

    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(binary_path, arcname=bin_name)

    checksum = sha256_file(package_path)
    checksum_file = RELEASE_DIR / f"{package_name}.sha256"
    checksum_file.write_text(f"{checksum}  {package_name}\n", encoding="utf-8")

    sign_with_gpg(checksum_file)

    print(f"[ok] package: {package_path}")
    print(f"[ok] sha256:  {checksum_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
