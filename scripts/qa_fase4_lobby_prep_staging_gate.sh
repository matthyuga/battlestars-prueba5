#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[QA-F4] Verificando flujo Lobby -> Room -> Staging -> Verify -> Duel..."

TARGET="game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy"
[[ -f "$TARGET" ]] || { echo "[FAIL] Falta archivo: $TARGET"; exit 1; }

# 1) Fase 2: separación física de screens room/staging
rg -n "screen bs_saga_preparation_room_screen\\(" "$TARGET" >/dev/null
rg -n "screen bs_saga_duel_staging_screen\\(" "$TARGET" >/dev/null
rg -n "call screen bs_saga_duel_staging_screen|call screen bs_saga_preparation_room_screen" "$TARGET" >/dev/null
echo "[QA-F4] OK: room/staging separados y enrutados."

# 2) Fase 3: contrato central precombat y checklist visible
rg -n "def bs_saga_precombat_contract_validate\\(" "$TARGET" >/dev/null
rg -n "Checklist pre-duelo|Bloqueantes:|Warnings:" "$TARGET" >/dev/null
echo "[QA-F4] OK: contrato precombat + checklist presentes."

# 3) Launch gate: no iniciar duelo con bloqueantes
rg -n "label bs_saga_launch_prepared_duel:" "$TARGET" >/dev/null
rg -n "bs_saga_precombat_contract_validate\\(\\)" "$TARGET" >/dev/null
rg -n "No puedes iniciar duelo" "$TARGET" >/dev/null
echo "[QA-F4] OK: launch gate bloqueante activo."

echo "[QA-F4] PASS"

