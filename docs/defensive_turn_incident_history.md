# Historial del incidente: crash al entrar al turno defensivo

## Estado actual (problema principal)

**Problema vigente:** al entrar al turno defensivo, el juego crashea con:

- `AttributeError: 'module' object has no attribute 'show_screen'`
- traceback apuntando a ejecución de `show screen battle_command_menu` en `battle_defensive_turn`.

Este problema se reportó tanto en `1v1` como en `2v2`.

---

## Línea de tiempo de acciones realizadas

> Objetivo del historial: tener trazabilidad de qué se cambió, por qué, y qué hipótesis se validaron/descartaron.

### 1) Migración inicial y aislamiento 2v2 (base)

- Se introdujo router por modo para labels públicas de turno.
- Se agregó `incoming_ctx` como SSOT para daño entrante/defensor.
- Se agregaron recursos por unidad y colas de daño diferido para 2v2.

**Resultado:** mejoras estructurales para 2v2, pero el crash de defensivo persistió incluso en 1v1.

---

### 2) Hardening de compatibilidad Ren'Py (R1)

- Se añadieron shims/wiring para APIs de `renpy` que podían faltar:
  - `get_screen`, `show_screen`, `hide_screen`, `restart_interaction`, `has_screen`.
- Se mantuvieron fallbacks seguros/no-op para evitar ruptura dura.

**Resultado:** mitigación parcial, pero no resolvió definitivamente el crash en runtime real del usuario.

---

### 3) Refactor de llamadas UI críticas (R2)

- Se crearon wrappers store-safe para UI:
  - `ui_show_screen_safe`, `ui_hide_screen_safe`.
- Se reemplazaron puntos críticos de `show/hide screen` statement-level en:
  - núcleo defensivo,
  - núcleo ofensivo,
  - flujo ofensivo enemigo (maniobra).
- Se migraron también pantallas de selección/inicio a wrappers safe.

**Resultado:** el código fuente quedó más robusto, pero el traceback del usuario siguió mostrando líneas legacy (`show screen ...`) en defensivo.

---

### 4) Refactor ampliado de runtime/UI (R3)

- Se extendió capa safe con:
  - `ui_get_screen_safe`,
  - `ui_has_screen_safe`,
  - `ui_restart_interaction_safe`.
- Se integró esa capa en:
  - visual log,
  - HUD update/show/hide,
  - turn change banner,
  - restart interaction en núcleos ofensivo/defensivo.

**Resultado:** cobertura más amplia de rutas UI, pero no cerró el caso en el entorno reportado.

---

### 5) Bootstrap temprano de APIs UI (R4)

- Se añadió `ensure_renpy_ui_apis()` (init temprano) para garantizar presencia de:
  - `renpy.show_screen`,
  - `renpy.hide_screen`,
  - `renpy.get_screen`,
  - `renpy.has_screen`,
  - `renpy.restart_interaction`.
- Se invocó además en entrypoints de combate (`start` y `battle_start`).

**Resultado:** mejora defensiva global, pero el usuario siguió viendo traceback con line mapping de bloque legacy.

---

### 6) Guard final de labels públicas + router interno (R4+)

- Se creó `zz_battle_label_guard.rpy` (carga tardía) para forzar que labels públicas de turno siempre pasen por router.
- Se renombraron entradas del router a `*_router_entry` para evitar solapamientos ambiguos.
- Se reforzó popup previo al defensivo en flujo enemigo para usar wrappers safe primero.

**Resultado:** se reduce riesgo de ejecución de rutas antiguas; aun así, el traceback reportado por usuario sigue apuntando a forma legacy.

---

## Diagnóstico consolidado (hipótesis principal)

### Hipótesis fuerte
Existe **desalineación entre el código fuente actual y el código efectivamente ejecutado** en el runtime de prueba:

- El fuente actual ya migró varios bloques a wrappers Python.
- El traceback del usuario sigue señalando statement-level `show screen ...` en líneas legacy.

Esto es compatible con:

1. build/caché desactualizada,
2. resolución de labels en ruta antigua,
3. mezcla de artefactos/runtime no sincronizados con el repo actual.

---

## Hallazgos de deuda técnica del repo

Se observa alta densidad de capas `legacy/fallback/compat` superpuestas en módulos clave:

- facade de estado,
- router/guards,
- fallbacks UI,
- núcleos de turno y HUD.

Esto aumenta:

- superficie de errores,
- dificultad de trazabilidad,
- riesgo de rutas solapadas en runtime.

---

## Acciones propuestas inmediatas (siguiente sesión)

1. Ejecutar **Fase 0 + Fase 1** del plan maestro (`docs/repo_cleanup_master_plan.md`).
2. Validar build limpia/caché limpia antes de QA manual.
3. Crear smoke mínimo reproducible (1v1 defensivo + 2v2 defensivo por slot).
4. Si el traceback sigue mostrando líneas legacy tras limpieza de build, auditar paquete de distribución (no solo repo fuente).

---

## Referencias relacionadas

- Plan maestro de limpieza: `docs/repo_cleanup_master_plan.md`.
- Router por modo: `game/4/00_BATTLE_MODE_ROUTER.rpy`.
- Guard final de labels públicas: `game/zz_battle_label_guard.rpy`.
- Núcleo defensivo actual: `game/4/j/04D_DEFENSIVE_CORE.rpy`.
- Capa de compat UI: `game/04a_battle_fallbacks_fxV2.rpy`.

