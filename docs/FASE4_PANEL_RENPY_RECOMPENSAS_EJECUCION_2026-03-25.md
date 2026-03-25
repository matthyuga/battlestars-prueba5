# Fase 4 — Integración de recompensas post-combate (Ren'Py)

Fecha: 2026-03-25  
Estado: completada (EXP/Oro integrados en runtime para simulación y QA).

## Alcance ejecutado

1. Core (`game/10A_RPG_PANEL_CORE_V1.rpy`):
   - Se agregó `compute_exp_oro_reward(...)`.
   - Se integraron multiplicadores de riesgo por ΔR (EXP/Oro), resultado (victoria/derrota), desempeño (estrellas) y anti-abuso por repetición.
   - Se agregó `reward_sim` al estado base y `reward_preview` calculado automáticamente en `compute_preview`.

2. UI (`game/10B_RPG_PANEL_UI_V1.rpy`):
   - Nuevo bloque “Recompensa post-combate (integración Fase 4)”.
   - Controles de simulación para QA rápida:
     - variar ΔR (rival register),
     - variar estrellas,
     - variar repetición,
     - alternar victoria/derrota.
   - Muestra en vivo `EXP final` y `Oro final`.

## Criterio de fase cubierto

- Recompensas derivadas en runtime desde funciones de cálculo, sin números hardcodeados en UI.

## Nota

La integración a flujo real de fin de combate (persistencia de recompensas en batalla real) puede abordarse como siguiente iteración técnica sobre esta base.
