# Fase A — Checkpoint de Cierre (Simulador V1)

> Estado: completado a nivel de contrato/motor base, listo para transición de fase.

---

## 1) Objetivo de la Fase A

Construir la base funcional del simulador sin UI de laboratorio completa:

- A1: contrato de entrada/salida.
- A2: validación dura de request.
- A3: núcleo matemático puro.
- A4: orquestador de simulación.
- A5: idempotencia por `reward_event_id`.
- A6: batería mínima de tests.
- A7: fixtures reproducibles.
- A8: cierre consolidado con checklist y changelog.

---

## 2) Entregables implementados

## 2.1 Código

Archivo principal:

- `game/10C_PROGRESSION_SIM_CONTRACT_V1.rpy`

Funciones clave:

- Contrato y validación:
  - `sim_build_min_request`
  - `sim_validate_request`
  - `sim_build_min_result`

- Núcleo matemático y orquestador:
  - `compute_stars_total`
  - `compute_delta_register`
  - `compute_performance_multipliers`
  - `compute_risk_multipliers`
  - `compute_multi_factor`
  - `compute_actor_reward`
  - `run_simulation`

- Idempotencia + pruebas/fixtures:
  - `sim_apply_reward_event_idempotency`
  - `sim_run_phaseA_tests`
  - `sim_phaseA_fixture_requests`
  - `sim_export_phaseA_fixtures_json`
  - `sim_phaseA_checkpoint_report`

## 2.2 Documentación

- `docs/BLUEPRINT_LAB_PROGRESION_CONTRATO_SIMULADOR_V1.md`
- `docs/GUIA_BALANCE_EXP_ORO_ESTRELLAS_V1.md`
- `docs/CONTRATO_SHADOW_LEDGER_REWARD_EVENT_ID_V1.md`
- `docs/CONTRATO_INVENTORY_PROFILE_UNIFICADO_V1.md`

---

## 3) Checklist A8 (estado)

- [x] `sim_contract_v1` estable.
- [x] `run_simulation()` funcional.
- [x] tests mínimos disponibles en runtime helper.
- [x] fixtures reproducibles disponibles.
- [x] changelog de parámetros disponible.

---

## 4) Changelog de parámetros (v1)

- `sim_contract_version = "v1"`
- Preset default: `medium_v2`
- Estrellas:
  - por categoría: `0..5`
  - total: `0..30`
- Registro: `0..50`
- Tablas riesgo ΔR:
  - EXP: `-5..+5 => 0.15..2.80`
  - Oro: `-5..+5 => 0.25..1.85`
- `m_multi = clamp((enemigos/aliados)^0.5, 0.85, 1.35)`
- Antiabuso por repetición:
  - rep1: `1.00`
  - rep2: `0.60`
  - rep3: `0.30`
  - rep>=4: `0.10`
- Idempotencia:
  - key: `reward_event_id|actor_id|source`
  - estados: `APPLY_OK`, `DUPLICATE_IGNORED`, `DUPLICATE_CONFLICT`

---

## 5) Riesgos / límites conocidos de Fase A

1. Persistencia de `idempotency_registry` delegada al caller (actualmente en memoria por diseño).
2. `level_after/register_after` aún conservador (sin pipeline de level-up completo).
3. Tests en formato runtime helper; falta integrar runner externo de CI dedicado.

---

## 6) Criterio de salida de fase

Fase A se considera cerrada cuando:

1. `sim_phaseA_checkpoint_report()` retorna `deliverables` completos.
2. La batería `sim_run_phaseA_tests()` no reporta fallos.
3. Fixtures y outputs exportables existen para diff de versiones.

---

## 7) Siguiente fase recomendada

Comenzar Fase B (UI mínima del laboratorio):

- selector de actores/equipos,
- editor de estrellas por categoría,
- botón de simulación + panel de resultado por actor,
- lectura del reporte de checkpoint.

