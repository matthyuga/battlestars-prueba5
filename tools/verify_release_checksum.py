#!/usr/bin/env python3
"""Verifica checksum SHA256 de un paquete release.

Uso:
  python tools/verify_release_checksum.py --package <zip> --checksum-file <zip.sha256>
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_checksum_file(path: Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError("checksum file vacío")
    parts = raw.split()
    if len(parts) < 2:
        raise ValueError("formato inválido, esperado '<sha256>  <filename>'")
    return parts[0].strip(), parts[-1].strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Verifica checksum SHA256 de paquete economy-toolkit.")
    ap.add_argument("--package", required=True, help="Ruta al zip descargado.")
    ap.add_argument("--checksum-file", required=True, help="Ruta al archivo .sha256.")
    args = ap.parse_args()

    package = Path(args.package)
    checksum_file = Path(args.checksum_file)

    if not package.exists():
        raise SystemExit(f"[error] package no existe: {package}")
    if not checksum_file.exists():
        raise SystemExit(f"[error] checksum file no existe: {checksum_file}")

    expected_sha, expected_name = parse_checksum_file(checksum_file)
    got_sha = sha256_file(package)

    if package.name != expected_name:
        print(f"[warn] el checksum espera '{expected_name}' pero package es '{package.name}'")

    if got_sha != expected_sha:
        print(f"[error] checksum inválido: expected={expected_sha} got={got_sha}")
        return 2

    print(f"[ok] checksum válido para {package.name}")
    print(f"[ok] sha256={got_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
