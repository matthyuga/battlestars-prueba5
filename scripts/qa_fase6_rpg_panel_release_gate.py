#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'game/10A_RPG_PANEL_CORE_V1.rpy'
UI = ROOT / 'game/10B_RPG_PANEL_UI_V1.rpy'
PLAN = ROOT / 'docs/PLAN_FASES_IMPLEMENTACION_PANEL_RENPY_V1.md'
DOC6 = ROOT / 'docs/FASE6_PANEL_RENPY_CIERRE_V1_2026-03-25.md'


def must(text, needle, msg):
    if needle not in text:
        raise AssertionError(msg)


def main():
    core = CORE.read_text(encoding='utf-8')
    ui = UI.read_text(encoding='utf-8')
    plan = PLAN.read_text(encoding='utf-8')
    doc6 = DOC6.read_text(encoding='utf-8')

    # DoD-oriented checks
    must(core, 'def rpgp_build_audit_snapshot', 'Falta builder de snapshot de auditoría')
    must(core, 'def rpgp_persist_audit_snapshot', 'Falta persistencia de snapshot de auditoría')
    must(ui, 'rpgp_build_audit_snapshot(st, source="panel_confirm_apply")', 'Confirm no genera snapshot')
    must(ui, 'rpgp_persist_audit_snapshot(snap)', 'Confirm no persiste snapshot')

    must(plan, 'Fase 6: completada', 'Plan no marca Fase 6 completada')
    must(doc6, 'Estado: completada', 'Documento Fase 6 no está completado')

    print('QA Fase6 RPG Panel Release Gate: OK')


if __name__ == '__main__':
    try:
        main()
    except AssertionError as e:
        print(f'QA Fase6 RPG Panel Release Gate: FAIL - {e}')
        sys.exit(1)
