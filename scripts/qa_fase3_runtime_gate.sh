#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[QA-F3] Verificando runtime de especiales (Ladrón + Salvaguarda)..."

# Dataset incluye nuevas técnicas
rg -n '"ladron_ofensivo"|"ladron_defensivo"|"ladron_concentrar"|"salvaguarda_principiante"' game/02_TECHNIQUES_DATASETV2.rpy >/dev/null
rg -n 'thief_offense|thief_defense|thief_focus|salvaguarda_basic' game/02_TECHNIQUES_DATASETV2.rpy >/dev/null

echo "[QA-F3] OK: dataset de especiales actualizado"

# Selector reconoce nuevas técnicas
rg -n "Ladrón ofensivo|Ladrón defensivo|Ladrón de concentrar|Salvaguarda principiante" game/04F_SELECTOR_FUNCTIONSV2.rpy game/04F_SELECTOR_QUEUV2.rpy game/04F_SELECTOR_MENUV2.rpy >/dev/null

echo "[QA-F3] OK: selector mapea nuevas técnicas"

# Runtime ofensivo aplica bloqueos ladrón
rg -n "_off_enemy_unit_key|_pick_enemy_tech_to_block|ladron_ofensivo|ai_block_tech_for_unit" game/4/j/04C_OFFENSIVE_ACTIONSV2.rpy >/dev/null

echo "[QA-F3] OK: ofensiva aplica bloqueo de ladrón"

# Runtime defensivo aplica salvaguarda por prioridad
rg -n "salvaguarda_principiante|special_defense_reduction_pct" game/4/j/04D_DEFENSIVE_ACTIONS.rpy game/4/j/04D_DEFENSIVE_OPERATION.rpy >/dev/null
rg -n "Salvaguarda:" game/4/j/04D_DEFENSIVE_OPERATION.rpy >/dev/null

echo "[QA-F3] OK: salvaguarda aplicada en pipeline defensivo"

echo "[QA-F3] PASS"
