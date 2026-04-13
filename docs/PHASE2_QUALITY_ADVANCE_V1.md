# Fase 2 — Calidad avanzada (Economy Toolkit)

Fecha: 2026-04-12

## Alcance implementado

1. **Golden/edge regression**
   - fixtures edge (`tests/golden/suite_old_edge.json`, `suite_new_edge.json`)
   - test de reglas borde del comparador (`tests/test_compare_golden_edge.py`)

2. **Stress/performance smoke**
   - test de rendimiento para `compare_suites` con 400 escenarios (`tests/test_compare_performance.py`)

3. **Harness e2e básico de wizard**
   - test del flujo guiado con entradas simuladas (`tests/test_wizard_flow.py`)

## Criterio de salida de Fase 2

- `python -m pytest -q` en verde con:
  - unit,
  - golden,
  - edge,
  - performance smoke,
  - wizard flow harness.

## Próximos incrementos sugeridos

- benchmark histórico y presupuesto de performance por versión,
- e2e del wizard en modo profile + verificación de artefactos reales,
- stress de comparador con 1k/5k escenarios en job nightly dedicado.
