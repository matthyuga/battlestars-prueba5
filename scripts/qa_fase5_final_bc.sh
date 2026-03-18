#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

./scripts/qa_fase3_runtime_gate.sh
./scripts/qa_fase5_precombat_gate.sh

echo "[QA-F5-BC] Verificando cierre documental QA-B/QA-C..."
rg -n "QA-B|QA-C|Validado|cerrado|fase 3" docs/FASE5_QA_CHECKPOINTS_2026-03-18.md >/dev/null

echo "[QA-F5-BC] PASS"
