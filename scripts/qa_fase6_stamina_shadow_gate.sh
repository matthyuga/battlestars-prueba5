#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[QA-F6] Ejecutando gates previos obligatorios..."
./scripts/qa_fase3_runtime_gate.sh
./scripts/qa_fase5_precombat_gate.sh

echo "[QA-F6] Ejecutando validación runtime de capas stamina/shadow..."
python3 ./scripts/qa_phase2_runtime_validation.py

echo "[QA-F6] Verificando contrato facade (APIs y logs canónicos)..."
rg -n "def bs_get_unit_stamina_shadow|def bs_set_unit_stamina_shadow|S\.bs_get_unit_stamina_shadow|S\.bs_set_unit_stamina_shadow" game/01B_BATTLE_STATE_FACADE.rpy >/dev/null
rg -n "Estamina: \{\} - \{\} =|HP genera \{\} de estamina|Shadow bloquea \{\} de espacio para estamina" game/01B_BATTLE_STATE_FACADE.rpy >/dev/null
rg -n "space\": \{|blocked_by_shadow" game/01B_BATTLE_STATE_FACADE.rpy >/dev/null

echo "[QA-F6] Verificando activación de perks en pre-combate -> runtime..."
rg -n "def precombat_resource_perks_snapshot|resource_perks" game/04I_PRECOMBAT_LOADOUT_SCREENV1.rpy >/dev/null
rg -n "Fase 5 — Activación Estamina/Shadow|bs_set_unit_stamina_shadow|\[PRECOMBAT\] Recursos" game/04b_battle_startV2.rpy >/dev/null

echo "[QA-F6] Verificando exposición HUD de estamina/shadow..."
rg -n "def hud_get_stamina_shadow_view|Estamina: \{\}/\{\}|Shadow: \{\}/\{\}|ST \{\}/\{\} · SH" game/06A_BATTLE_HUD_SYSTEMV2.rpy >/dev/null

echo "[QA-F6] PASS"
