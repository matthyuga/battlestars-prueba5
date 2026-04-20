# Ejecución — Fase 0 + Fase 1 (C4 recompensas)

Fecha: 2026-04-20  
Estado: Fase 0 completada (baseline técnico) + Fase 1 completada (diseño funcional)

---

## Contexto
Este documento ejecuta las fases definidas en:
- `docs/PLAN_FASES_IMPLEMENTACION_POSTCOMBATE_Y_VICTORIA_INSTANTANEA_2026-04-20.md`

Alcance de esta entrega:
1. **Fase 0:** baseline reproducible del estado actual de C4.
2. **Fase 1:** especificación funcional para arrancar implementación C4 v2.

---

## Fase 0 — Baseline técnico del estado actual

### 0.1 Flujo canónico actual
Secuencia observada en código:
1. `label battle_end` arma `runtime`.
2. Ejecuta simulación (`sim_run_battle_end_simulation`).
3. Persiste artefactos (`sim_persist_simulation_artifacts`).
4. Aplica recompensas (`sim_apply_simulation_rewards_to_runtime`).
5. Muestra `sim_battle_end_reward_summary_v1`.

Fuente: `game/04e_battle_end_result.rpy`.

### 0.2 Campos visibles actuales en pantalla C4
- Header: `sim_id`, `mode`, `winner`.
- Aplicación: `ok`, `count`, `EXP`, `Oro`.
- Auditoría: `warnings`, `errors`.
- Filas actor por actor: `actor_id`, `outcome`, `eligible`, `EXP +x`, `Oro +y`.

Fuente: `screen sim_battle_end_reward_summary_v1`.

### 0.3 Hallazgo UX confirmado
La pantalla lista también filas de enemigo/actores no elegibles, por eso aparecen líneas como `EXP +0 | Oro +0`. Técnicamente es correcto (resultado completo), pero para UX de jugador genera ruido.

### 0.4 Baseline de datos para explicabilidad (ya disponible)
El cálculo de recompensa ya expone:
- `base` (exp/oro)
- `multipliers` (risk/result/performance/antiabuso/multi_factor/hp/condiciones)
- `delta_register`, `stars_total`, `final` (exp_gain/oro_gain)

Fuente: `compute_actor_reward`.

### 0.5 Resultado de Fase 0
✅ Baseline técnico completado y trazado.  
⚠️ Baseline visual en runtime (capturas de 3 escenarios) queda como verificación manual en QA interactivo.

---

## Fase 1 — Diseño funcional C4 v2

### 1.1 Objetivo UX
Mostrar de forma prioritaria **la recompensa obtenida por el jugador/equipo propio** y dejar el detalle técnico accesible pero secundario.

### 1.2 Estructura funcional aprobada para implementación

#### Bloque A — Resultado principal (siempre visible)
- Título: “Recompensa obtenida”.
- KPIs: EXP ganada, Oro ganado, `applied_count`.
- Estado corto: `ok/warnings/errors`.

#### Bloque B — Parámetros de rendimiento (visible por defecto)
- Base EXP/Oro.
- Multiplicadores principales:
  - `risk_exp/risk_oro`
  - `result_exp/result_oro`
  - `performance_exp/performance_oro`
  - `antiabuso`, `multi_factor`
  - `hp_reward_multiplier`
  - `reward_condition_exp_mult/reward_condition_oro_mult`
- Fórmulas textuales (exp y oro) para explicar cómo se llegó al final.

#### Bloque C — Detalle técnico (colapsable)
- Tabla completa de actores (`results[]`).
- Warnings y errores de auditoría.
- Toggle QA: “Mostrar actores no elegibles / +0”.

### 1.3 Reglas de visibilidad
1. Default jugador:
   - Ocultar filas `eligible=False` **o** (`exp_gain=0` y `oro_gain=0`).
2. Default QA/dev:
   - Mostrar toggle para ver dataset completo.
3. Errores/warnings:
   - Siempre visibles (nunca ocultarlos detrás de toggle).

### 1.4 Requisitos no funcionales
- No alterar contrato de simulación ni pipeline de negocio.
- No romper compatibilidad con `mid_battle` + reconciliación en `battle_end`.
- Mantener navegación actual (`Continuar` y retorno de flujo).

### 1.5 Definición de listo para pasar a Fase 2
- Wireframe funcional textual cerrado.
- Reglas de visibilidad cerradas.
- Lista de campos/fórmulas cerrada.
- Sin cambios de balance económico.

### 1.6 Resultado de Fase 1
✅ Fase 1 completada y lista para implementación.

---

## Confirmación de avance
Con esta entrega, **Fase 0 y Fase 1 quedan listas** para iniciar **Fase 2 (implementación C4 v2)**.

Siguiente paso recomendado:
1. Refactor de `screen sim_battle_end_reward_summary_v1`.
2. Agregar bloque “Parámetros de rendimiento”.
3. Añadir toggle QA de filas no elegibles.
