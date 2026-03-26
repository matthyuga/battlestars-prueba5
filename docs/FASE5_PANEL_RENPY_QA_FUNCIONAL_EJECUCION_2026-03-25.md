# Fase 5 — QA funcional del panel RPG (Ren'Py)

Fecha: 2026-03-25  
Estado: completada.

## Alcance de QA ejecutado

Se ejecutó un gate automático de consistencia para el panel RPG v1:

- Script: `scripts/qa_fase5_rpg_panel_gate.py`

Cobertura del gate:

1. Presencia de funciones clave en core:
   - `compute_register`
   - `compute_pool_total`
   - `compute_stat_effects`
   - `compute_principal_bonus`
   - `compute_caps_for_register`
   - `compute_consumption_at_cap`
   - `compute_exp_oro_reward`
   - `compute_preview`
   - `validate_panel_state`

2. Presencia de bloques mínimos en UI:
   - `screen rpg_panel_v1`
   - `screen rpg_panel_confirm_modal_v1`
   - bloque de recompensa Fase 4

3. Checks numéricos de regresión:
   - Caps Reg0/Reg10/Reg35 (PVE/PVP) contra valores esperados de planilla.
   - Recompensas EXP/Oro en casos de referencia de fórmula.

4. Verificación de anclas documentales:
   - planilla de caps
   - planilla de recompensas

## Resultado

- Gate ejecutado en verde (`QA Fase5 RPG Panel: OK`).

## Nota

Este QA valida consistencia funcional/matemática base y regresión de contrato.
No reemplaza pruebas manuales visuales de UX final o arte.
