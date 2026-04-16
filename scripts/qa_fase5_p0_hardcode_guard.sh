#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

HUB_FILE="game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy"
DEFS_FILE="game/00_definitions_charactersV2.rpy"
SELECTOR_FILE="game/04A_BATTLE_CHARACTER_SELECTV3.rpy"

echo "[QA-F5-P0] Verificando guardas anti-hardcode (A/B)..."

if ! rg -q "def bs_saga_resolve_roster_v1" "$HUB_FILE"; then
  echo "[QA-F5-P0] FAIL: falta resolver unificado de roster en Hub."
  exit 1
fi
echo "[QA-F5-P0] OK: resolver unificado presente."

if ! rg -q 'getattr\(S, "bs_saga_resolve_roster_v1"' "$DEFS_FILE"; then
  echo "[QA-F5-P0] FAIL: get_combat_character_ids no prioriza resolver unificado."
  exit 1
fi
echo "[QA-F5-P0] OK: runtime prioriza resolver unificado."

if ! rg -q "screen battle_select_dynamic_list_screen" "$SELECTOR_FILE"; then
  echo "[QA-F5-P0] FAIL: selector dinámico no encontrado."
  exit 1
fi
echo "[QA-F5-P0] OK: selector dinámico presente."

if rg -q '"Harribel"|"Grimmjow"|"Nel"|"Hollow"' "$SELECTOR_FILE"; then
  echo "[QA-F5-P0] FAIL: quedan héroes hardcodeados en selector legacy."
  exit 1
fi
echo "[QA-F5-P0] OK: sin héroes hardcodeados en selector legacy."

if [[ ! -f "game/data/item_catalog_v1.json" ]] || [[ ! -f "game/data/tech_catalog_v1.json" ]]; then
  echo "[QA-F5-P0] FAIL: faltan contratos JSON versionables para catálogos."
  exit 1
fi
echo "[QA-F5-P0] OK: contratos JSON presentes."

if rg -Fq '"Poción HP roja"' "$HUB_FILE" || rg -Fq '"Ataque negador"' "$HUB_FILE"; then
  echo "[QA-F5-P0] FAIL: catálogo inline detectado en HUB (bloque C incompleto)."
  exit 1
fi
echo "[QA-F5-P0] OK: catálogos inline retirados del HUB."

echo "[QA-F5-P0] PASS"
