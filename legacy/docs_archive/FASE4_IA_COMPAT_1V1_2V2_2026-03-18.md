# Fase 4 — IA y compatibilidad 1v1/2v2 (2026-03-18)

## Estado
**Implementada (corte inicial)** para reglas de bloqueo en planificador/ejecutor IA.

---

## Cambios aplicados

1. **Infraestructura de bloqueo por unidad (`unit_key`)**
   - Se agregó almacenamiento de bloqueos por unidad/técnica.
   - API base:
     - `ai_block_tech_for_unit(unit_key, tech_id, turns, phase)`
     - `ai_is_tech_blocked(unit_key, tech_id, phase, consume)`
     - `ai_filter_blocked_plan(plan, unit_key, forced, phase)`

2. **Regla IA en plan ofensivo/defensivo**
   - En modo **forzado**: no reemplaza técnica bloqueada (se mantiene en plan).
   - En modo **normal/concat**: omite técnica bloqueada y continúa con el resto válido.

3. **Regla IA en ejecución (runtime de IA)**
   - Si la acción del plan está bloqueada para la unidad actual:
     - se loguea bloqueo,
     - se omite la ejecución de esa acción,
     - se consume la ventana de bloqueo (1 turno aplicable).

4. **Compatibilidad por unidad para 1v1/2v2**
   - Resolución por `current_enemy_unit_key`/`ai_get_current_enemy_unit_key`.
   - Diseño preparado para objetivo por slot en modos múltiples.

---

## Archivos

- `game/4/04D_AI_PLANS_COREV1.rpy`
- `game/4/04D_AI_PLANS_OFFENSEV1a.rpy`
- `game/4/04D_AI_PLANS_DEFENSEV1a.rpy`
- `game/4/04D_AI_EXECUTIONV5.rpy`

---

## Alcance y nota importante

- Este corte cubre reglas de Fase 4 del lado IA.
- La mecánica completa de selección/bloqueo de técnicas “Ladrón ...” en flujo de combate sigue dependiendo del runtime profundo de especiales (Fase 3).
