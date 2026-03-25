# Fase 1 — Ejecución del core de cálculo (Ren'Py)

Fecha: 2026-03-25
Estado: completada (core funcional inicial).

## Alcance ejecutado

Se implementó el módulo `game/10A_RPG_PANEL_CORE_V1.rpy` con:

1. Constantes y reglas núcleo del contrato.
2. Constructor de estado por defecto (`_rpgp_default_state`).
3. API de cálculo:
   - `compute_register`
   - `compute_pool_total`
   - `compute_stat_effects`
   - `compute_principal_bonus`
   - `compute_caps_for_register`
   - `compute_preview`
   - `validate_panel_state`
4. Semillas de QA:
   - `rpgp_seed_new_player`
   - `rpgp_seed_reg10_balanced`
   - `rpgp_seed_reg35_specialized`
5. Labels de bootstrap/debug para cargar semillas en runtime.

## Validaciones bloqueantes implementadas

- principal obligatorio
- distribución del principal = 100
- máximo 4 categorías activas del principal
- gasto total de pool <= disponible
- respeto de caps por tier/modo en ofensiva y defensiva

## Observaciones

- Esta fase implementa únicamente el motor de cálculo y helpers de estado.
- No incluye pantalla final de producción (eso corresponde a Fase 2).

