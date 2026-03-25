# Checklist de sesión — Smoke 1v1 defensivo (build limpia)

## Objetivo único de la sesión

Resolver y validar el bug crítico:

- crash al entrar al turno defensivo,
- `AttributeError: 'module' object has no attribute 'show_screen'`,
- reproducible en `1v1` (y también reportado en `2v2`).

---

## Fuentes oficiales obligatorias

Antes de ejecutar, leer y tomar como referencia principal:

1. `docs/repo_cleanup_master_plan.md`
2. `docs/defensive_turn_incident_history.md`

---

## Reglas operativas (no negociables)

- Ejecutar por fases, sin improvisar sobre features nuevas.
- En esta sesión: **solo Fase 0 + Fase 1**.
- No introducir nuevas features 2v2.
- Toda validación manual debe realizarse con build/caché limpia.

---

## Fase 0 — Baseline técnica reproducible

### 0.1 Snapshot mínimo (rápido)

- [ ] Confirmar labels públicas de turno:
  - `battle_offensive_turn`
  - `battle_enemy_turn`
  - `battle_defensive_turn`
- [ ] Confirmar ruta esperada en `1v1`:
  - pública -> router -> `*_1v1_entry` -> `*_legacy_entry`
- [ ] Confirmar dependencias críticas defensivas:
  - `battle_popup_turn`
  - `battle_command_menu`
  - `ui_show_screen_safe`
  - `ui_hide_screen_safe`
  - `ui_restart_interaction_safe`

### 0.2 Higiene de build/caché

- [ ] Cerrar juego/runtime.
- [ ] Limpiar artefactos de cache/compilación Ren'Py del proyecto.
- [ ] Reabrir/recompilar proyecto.
- [ ] Confirmar que el runtime corresponde al commit actual.

> Nota: si no se limpia caché, el traceback puede seguir apuntando a rutas legacy no alineadas con fuente.

---

## Fase 1 — Validación 1v1 (línea de vida)

### 1.1 Verificación de trazabilidad de rutas

- [ ] Iniciar combate en modo `1v1`.
- [ ] Confirmar en logs una traza tipo:
  - `ROUTE mode=1v1 owner=... label=...`
- [ ] Verificar que el turno defensivo entra por la ruta esperada de `1v1`.

### 1.2 Smoke funcional 1v1 defensivo (obligatorio)

Escenario base:

1. [ ] Enemigo ataca al jugador.
2. [ ] El flujo entra al turno defensivo.
3. [ ] Probar **defensa normal**.
4. [ ] Probar **maniobra defensiva por ataque**.

Criterios de aprobación:

- [ ] No ocurre crash.
- [ ] No aparece `AttributeError: renpy.show_screen`.
- [ ] Menús defensivos se muestran/ocultan correctamente.
- [ ] Se resuelve daño y el turno retorna al flujo normal.

---

## Smoke de vigilancia (solo control de regresión)

> No es objetivo principal de esta sesión, pero sí una verificación rápida de no ruptura accidental.

- [ ] Iniciar combate `2v2`.
- [ ] Forzar daño entrante a slot específico de jugador.
- [ ] Verificar entrada al defensivo del slot correcto.

---

## Criterio de salida de sesión

La sesión se considera exitosa solo si:

- [ ] `1v1` defensivo es estable en build limpia.
- [ ] No hay crash por `renpy.show_screen`.
- [ ] Se documenta smoke reproducible con evidencia mínima (pasos + resultado + commit/hash probado).

---

## Plantilla de reporte rápido (copiar/pegar)

```md
## Smoke defensivo 1v1 — <YYYY-MM-DD HH:MM>
Commit probado: <hash>
Build/caché limpia: Sí/No
Ruta observada en logs: <ROUTE mode=1v1 ...>

Caso A (defensa normal): PASS/FAIL
Caso B (maniobra defensiva): PASS/FAIL

¿Crash?: Sí/No
Traceback (si aplica): <pegar>

Resultado final sesión: PASS/FAIL
Notas: <detalles>
```

---

## Escalamiento si persiste el crash

Si después de build limpia el traceback sigue apuntando a líneas legacy:

- [ ] Auditar el paquete de distribución/build ejecutado (no solo el repo fuente).
- [ ] Verificar mapeo archivo/línea del traceback contra el commit vigente.
- [ ] Detener nuevas capas de parche hasta cerrar causa raíz.
