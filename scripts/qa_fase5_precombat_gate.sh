#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[QA-F5] Verificando artefactos de fases 1/2/4..."

# 1) Archivos clave presentes
required_files=(
  "game/04I_PRECOMBAT_LOADOUT_SCREENV1.rpy"
  "game/4/04D_AI_PLANS_COREV1.rpy"
  "game/4/04D_AI_PLANS_OFFENSEV1a.rpy"
  "game/4/04D_AI_PLANS_DEFENSEV1a.rpy"
  "game/4/04D_AI_EXECUTIONV5.rpy"
  "docs/FASE1_ARRANQUE_PRECOMBATE_2026-03-18.md"
  "docs/FASE2_UI_ESCALABILIDAD_2026-03-18.md"
  "docs/FASE4_IA_COMPAT_1V1_2V2_2026-03-18.md"
)
for f in "${required_files[@]}"; do
  [[ -f "$f" ]] || { echo "[FAIL] Falta archivo: $f"; exit 1; }
done

echo "[QA-F5] OK: archivos clave presentes"

# 2) Contratos mínimos pre-combate
rg -n "precombat_validate_current|precombat_confirm_selection|precombat_save_profile|precombat_load_profile" game/04I_PRECOMBAT_LOADOUT_SCREENV1.rpy >/dev/null
rg -n "modo por slots|modo libre|extra_spc_slots|paginación|íconos|fallback" docs/FASE2_UI_ESCALABILIDAD_2026-03-18.md >/dev/null

echo "[QA-F5] OK: contratos pre-combate detectados"

# 3) Contratos mínimos IA fase 4
rg -n "ai_block_tech_for_unit|ai_is_tech_blocked|ai_filter_blocked_plan" game/4/04D_AI_PLANS_COREV1.rpy >/dev/null
rg -n "forced_mode|ai_filter_blocked_plan" game/4/04D_AI_PLANS_OFFENSEV1a.rpy game/4/04D_AI_PLANS_DEFENSEV1a.rpy >/dev/null
rg -n "bloqueada por 1 turno|_ai_is_blocked_for_enemy" game/4/04D_AI_EXECUTIONV5.rpy >/dev/null

echo "[QA-F5] OK: contratos IA fase 4 detectados"

# 4) Estado documental del roadmap
rg -n "Fase 5|QA incremental" docs/PLAN_FASES_PRECOMBATE_TECNICAS_ESPECIALES.md >/dev/null

echo "[QA-F5] OK: roadmap contiene fase QA incremental"

echo "[QA-F5] PASS"
