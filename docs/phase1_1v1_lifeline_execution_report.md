# Fase 1 — Reporte de ejecución (línea de vida 1v1)

Estado: **completada (código + validaciones estáticas)**
Fecha: _actualizar en QA manual_

## Objetivo de Fase 1

Aislar el camino `1v1` para que no dependa accidentalmente de contexto `2v2` y mantener trazabilidad clara de routing por turno.

---

## Cambios aplicados

### 1) Preparación explícita de entrada 1v1

En `game/4/00_BATTLE_MODE_1V1_ENTRY.rpy` se agregó `bs_prepare_1v1_turn_entry(owner=...)` que, antes de cada turno 1v1:

- fuerza `battle_team_mode = "1v1"`,
- limpia residuos de target defensivo/incoming (`incoming_damage_target_key`, `defense_target_key`),
- limpia `incoming_ctx` mediante `bs_clear_incoming_ctx()` si existe,
- fija `turn_owner_team` y `turn_owner_slot = 0`,
- emite log de preparación `ROUTE_PREP mode=1v1 ...`.

### 2) Integración en los 3 entrypoints 1v1

Se invoca la preparación en:

- `battle_offensive_turn_1v1_entry`
- `battle_enemy_turn_1v1_entry`
- `battle_defensive_turn_1v1_entry`

Manteniendo además el log de trazabilidad de ruta:

- `ROUTE mode=1v1 owner=... label=...`.

---

## Justificación técnica

Esto cumple el punto clave de Fase 1 del plan maestro:

> asegurar que `battle_team_mode == 1v1` no consuma colas/contexto por unidad de `2v2` en el flujo de turnos.

La limpieza se hace en el borde de entrada (`*_1v1_entry`) para que el legacy interno pueda seguir estable mientras se avanza con fases posteriores.

---

## Validaciones ejecutadas

### Validación de símbolo y llamadas

- Existe `bs_prepare_1v1_turn_entry` en módulo 1v1.
- Los tres labels `*_1v1_entry` llaman la preparación antes del `jump`.
- Se conserva el log `ROUTE mode=1v1 ...` por turno.

### Validación de contrato de router

- `battle_*_turn_router_entry` sigue enroutando `1v1` a `*_1v1_entry`.

---

## Criterio de salida de Fase 1

- [x] Camino 1v1 explícito y trazable.
- [x] Preparación de estado para evitar acoplamiento accidental con contexto 2v2.
- [x] Sin introducir nuevas features 2v2.
- [ ] Smoke runtime manual en build limpia (pendiente de ejecución en entorno de juego).

---

## Siguiente paso recomendado

Ejecutar smoke manual con la checklist:

- `docs/session_smoke_checklist_1v1.md`

y registrar resultado usando la plantilla de reporte incluida allí.
