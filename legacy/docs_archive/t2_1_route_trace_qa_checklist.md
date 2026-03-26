# T2.1 — Checklist de trazabilidad de rutas (debug)

## Objetivo
Validar en runtime que la secuencia de turnos no tenga saltos ambiguos y que el router respete el contrato público:

- `battle_offensive_turn`
- `battle_enemy_turn`
- `battle_defensive_turn`

con logging uniforme:

`ROUTE mode=<1v1|2v2> phase=<off|enemy|def> owner=<unit> target=<slot|auto>`

---

## Preparación

1. Iniciar sesión limpia (sin cache/build stale, si aplica en tu flujo QA).
2. En consola de debug de Ren'Py, activar:

```python
battle_debug_routes = True
```

3. Confirmar que existe logger:

```python
callable(getattr(renpy.store, "battle_log_add", None))
```

---

## Escenario A — Smoke 1v1 (obligatorio)

### Pasos
1. Forzar/asegurar `battle_team_mode = "1v1"`.
2. Jugar una ronda completa (off -> enemy -> def).
3. Repetir una segunda ronda para descartar estado sucio.

### Secuencia esperada (orden)
1. `ROUTE mode=1v1 phase=off owner=player target=auto label=battle_offensive_turn_router_entry`
2. `ROUTE mode=1v1 phase=off owner=player target=auto label=battle_offensive_turn_legacy_entry`
3. `ROUTE mode=1v1 phase=enemy owner=enemy target=auto label=battle_enemy_turn_router_entry`
4. `ROUTE mode=1v1 phase=enemy owner=enemy target=auto label=battle_enemy_turn_legacy_entry`
5. `ROUTE mode=1v1 phase=def owner=player target=auto label=battle_defensive_turn_router_entry`
6. `ROUTE mode=1v1 phase=def owner=player target=auto label=battle_defensive_turn_legacy_entry`

### Criterio de aceptación
- No faltan fases (`off`, `enemy`, `def`).
- No aparece doble salto inesperado de phase/owner.
- No hay freeze silencioso entre `enemy -> def`.

---

## Escenario B — Smoke 2v2 (stub actual)

### Pasos
1. Forzar/asegurar `battle_team_mode = "2v2"`.
2. Ejecutar una ronda completa con target explícito (slot 0 o 1).

### Secuencia esperada (mínima)
- Entradas router y delegación legacy en cada fase con `target=slot`.

### Criterio de aceptación
- `mode=2v2` se mantiene coherente en toda la secuencia.
- Cada fase muestra router + legacy entry correspondiente.

---

## Diagnóstico rápido si falla

- Si falta cualquier log `ROUTE ...`, verificar que `battle_debug_routes` siga en `True`.
- Si logs aparecen desordenados con labels inexistentes, limpiar cache/build y repetir.
- Si se congela tras `phase=enemy`, registrar última línea `ROUTE` y stack trace para T3/T4.

---

## Cierre de sesión QA

Desactivar trazas:

```python
battle_debug_routes = False
```

Guardar extracto de log con:
- modo probado,
- secuencia observada,
- último `ROUTE` antes de cualquier error.
