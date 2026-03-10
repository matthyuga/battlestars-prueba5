#!/usr/bin/env python3
"""Validación rápida de assets HUD/GUI para el proyecto Ren'Py.

Uso:
  python scripts/validate_hud_assets.py

Qué valida:
1) Presencia de assets esperados para HUD IA (frames, icons, portraits).
2) Referencias a imágenes en archivos .rpy que apunten a archivos inexistentes.

Exit code:
- 0: sin faltantes.
- 1: se encontraron faltantes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME_DIR = ROOT / "game"


def check_hud_ai_assets() -> list[str]:
    missing: list[str] = []

    styles = ["carmesi", "fantasy", "grey", "virtual"]
    modes = ["stat", "option"]
    for style in styles:
        for mode in modes:
            p = ROOT / "game" / "gui" / "battle" / "hud_ai" / "frames" / f"frame_{style}_{mode}.png"
            if not p.exists():
                missing.append(str(p.relative_to(ROOT)))

    for icon in [
        "icon_style_picker_arrow_gold",
        "icon_panel_swap_blue",
        "icon_panel_close_red",
    ]:
        p = ROOT / "game" / "gui" / "battle" / "hud_ai" / "icons" / f"{icon}.png"
        if not p.exists():
            missing.append(str(p.relative_to(ROOT)))

    for char in ["harribel", "hollow", "grimmjow", "nel"]:
        for variant in ["head", "full", "token"]:
            p = ROOT / "game" / "gui" / "battle" / "hud_ai" / "portraits" / f"portrait_{char}_{variant}.png"
            if not p.exists():
                missing.append(str(p.relative_to(ROOT)))

    return missing


def check_missing_image_refs_in_rpy() -> list[tuple[str, str]]:
    pattern = re.compile(r'"([^"\n]+\.(?:png|jpg|jpeg|webp))"', re.IGNORECASE)
    missing: list[tuple[str, str]] = []

    for rpy_file in GAME_DIR.rglob("*.rpy"):
        text = rpy_file.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            image_ref = m.group(1)
            # Ignora rutas dinámicas/listas no resolubles estáticamente aquí.
            if "{" in image_ref or "[" in image_ref:
                continue

            candidates = [ROOT / image_ref, GAME_DIR / image_ref]
            if not any(c.exists() for c in candidates):
                missing.append((str(rpy_file.relative_to(ROOT)), image_ref))

    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida assets HUD/GUI en el proyecto.")
    parser.add_argument("--only-hud-ai", action="store_true", help="Solo valida frames/icons/portraits de HUD IA.")
    parser.add_argument("--allow-missing", action="append", default=[], metavar="RUTA", help="Permite una referencia faltante específica (ej. gui/confirm_frame.png). Repetible.")
    args = parser.parse_args()

    hud_missing = check_hud_ai_assets()
    ref_missing = [] if args.only_hud_ai else check_missing_image_refs_in_rpy()

    allowed = set(args.allow_missing or [])
    if allowed:
        ref_missing = [(f, img) for (f, img) in ref_missing if img not in allowed]

    print("=== Validación rápida HUD/GUI ===")

    print(f"\n[HUD AI] faltantes: {len(hud_missing)}")
    for item in hud_missing:
        print(f"  - {item}")

    if args.only_hud_ai:
        print("\n[Refs .rpy -> imagen] omitido por --only-hud-ai")
    else:
        print(f"\n[Refs .rpy -> imagen] faltantes: {len(ref_missing)}")
        for file_path, img in ref_missing:
            print(f"  - {file_path}: {img}")

    total = len(hud_missing) + len(ref_missing)
    if total == 0:
        print("\nOK: no se detectaron faltantes.")
        return 0

    print(f"\nERROR: se detectaron {total} faltantes en total.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
