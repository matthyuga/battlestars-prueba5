# Fase 0 + Fase 1 — Inventario baseline y línea de vida 1v1

## Alcance de esta sesión

- **Fase 0:** inventario de labels/rutas activas y smoke baseline reproducible.
- **Fase 1:** congelar entrada `1v1` en rutas explícitas, separadas de decisiones de enrutado `2v2`.

---

## 1) Snapshot de labels públicas y resolución de rutas

### Labels públicas (contrato)

- `battle_offensive_turn`
- `battle_enemy_turn`
- `battle_defensive_turn`

### Resolución actual

1. Labels públicas (`game/zz_battle_label_guard.rpy`) redirigen al router.
2. Router (`game/4/00_BATTLE_MODE_ROUTER.rpy`) decide por `battle_team_mode`:
   - `2v2` -> `*_2v2_entry`
   - `1v1` -> `*_1v1_entry`
3. Entradas `*_1v1_entry` (`game/4/00_BATTLE_MODE_1V1_ENTRY.rpy`) saltan a labels legacy estables:
   - `battle_offensive_turn_legacy_entry`
   - `battle_enemy_turn_legacy_entry`
   - `battle_defensive_turn_legacy_entry`

---

## 2) Inventario de hotspots legacy/fallback/compat

### Archivos con densidad alta de compat/UI safe wrappers

- `game/04a_battle_fallbacks_fxV2.rpy`
- `game/4/00_BATTLE_MODE_ROUTER.rpy`
- `game/zz_battle_label_guard.rpy`
- `game/4/j/04D_DEFENSIVE_CORE.rpy`
- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`

### Dependencias críticas (objetivo defensivo)

- `battle_defensive_turn` (pública)
- `battle_defensive_turn_router_entry` (router)
- `battle_defensive_turn_1v1_entry` (línea de vida 1v1)
- `battle_defensive_turn_legacy_entry` (núcleo defensivo)
- `battle_popup_turn`
- `battle_command_menu`
- API UI safe:
  - `ensure_renpy_ui_apis`
  - `ui_show_screen_safe`
  - `ui_hide_screen_safe`
  - `ui_restart_interaction_safe`

---

## 3) Smoke baseline obligatorio (build/caché limpia)

> Regla de QA: ejecutar siempre sobre build limpia para evitar tracebacks desde artefactos legacy.

### Pre-condición técnica

1. Limpiar artefactos de compilación/caché de Ren'Py del proyecto.
2. Recompilar/reabrir proyecto.
3. Confirmar que los logs de ruta muestran `ROUTE mode=1v1 ...` al entrar a turnos en 1v1.

### Smoke A — 1v1 defensivo (criterio principal)

1. Iniciar combate `1v1`.
2. Forzar ataque enemigo al jugador.
3. Entrar al turno defensivo.
4. Probar ambas decisiones:
   - defensa normal,
   - maniobra defensiva por ataque.
5. Confirmar:
   - no hay crash,
   - se muestran/ocultan menús defensivos,
   - el turno resuelve daño y retorna al flujo.

### Smoke B — 2v2 defensivo por slot (solo vigilancia)

1. Iniciar combate `2v2`.
2. Forzar daño entrante a slot específico de jugador.
3. Verificar que el turno defensivo entra con contexto de slot correcto.

---

## 4) Criterio de éxito operativo

- `1v1` defensivo estable en build limpia.
- Sin `AttributeError: renpy.show_screen` en entrada/resolución defensiva.
- Smoke mínimo documentado y reproducible por cualquier dev.
