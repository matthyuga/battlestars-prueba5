# Fase 0 — Reporte de ejecución (inventario y baseline)

Estado: **completada**
Fecha: _actualizar en QA manual_

## Objetivo de Fase 0

Congelar una foto técnica del flujo de turnos, dependencias críticas y smoke mínimo reproducible para evitar más parches superpuestos sin baseline estable.

---

## 1) Snapshot de labels públicas y cadena de resolución

### Labels públicas detectadas

- `battle_offensive_turn`
- `battle_enemy_turn`
- `battle_defensive_turn`

Definidas en `game/zz_battle_label_guard.rpy` y redirigidas al router por modo.

### Cadena de resolución actual

1. `battle_*_turn` (pública)
2. `battle_*_turn_router_entry`
3. `battle_*_turn_1v1_entry` cuando `battle_team_mode == "1v1"`
4. `battle_*_turn_legacy_entry` (implementación actual estable)

Notas:

- `2v2` sigue en stubs que delegan a legacy (no se amplía alcance en esta fase).
- Se mantiene trazabilidad por logs de ruta para `1v1`.

---

## 2) Dependencias críticas del incidente defensivo

- Núcleo defensivo: `game/4/j/04D_DEFENSIVE_CORE.rpy`
- Router por modo: `game/4/00_BATTLE_MODE_ROUTER.rpy`
- Guard tardío de labels públicas: `game/zz_battle_label_guard.rpy`
- Wrappers/UI safe y wiring:
  - `game/04a_battle_fallbacks_fxV2.rpy`
  - `game/00_GLOBALS_SYSTEMV3.rpy`

### Riesgo principal vigente

El historial mantiene como hipótesis fuerte la desalineación fuente/runtime cuando se valida con build/caché stale.

---

## 3) Inventario de hotspots legacy/fallback/compat

Hotspots activos priorizados:

1. `game/04a_battle_fallbacks_fxV2.rpy`
2. `game/00_GLOBALS_SYSTEMV3.rpy`
3. `game/4/j/04D_DEFENSIVE_CORE.rpy`
4. `game/4/00_BATTLE_MODE_ROUTER.rpy`
5. `game/zz_battle_label_guard.rpy`

Criterio usado: densidad de wrappers, wiring de APIs de `renpy`, routing y puntos de entrada del turno defensivo.

---

## 4) Smoke baseline (definición oficial de sesión)

### Precondición obligatoria

- Ejecutar QA manual con build/caché limpia.

### Smoke principal (1v1)

1. Ataque enemigo al jugador.
2. Entrada a turno defensivo.
3. Probar defensa normal.
4. Probar maniobra defensiva por ataque.
5. Verificar ausencia de crash y retorno de flujo.

### Smoke vigilancia (2v2)

1. Daño entrante en slot específico.
2. Verificar entrada defensiva del slot correcto.

---

## 5) Evidencia de inventario (comandos usados)

```bash
rg -n "label battle_(offensive|enemy|defensive)_turn\b|label battle_(offensive|enemy|defensive)_turn_router_entry|label battle_(offensive|enemy|defensive)_turn_1v1_entry|label battle_(offensive|enemy|defensive)_turn_legacy_entry|show screen battle_command_menu|ui_show_screen_safe|ensure_renpy_ui_apis" game docs
```

---

## 6) Criterio de salida Fase 0

- [x] Snapshot de rutas documentado.
- [x] Dependencias críticas listadas.
- [x] Hotspots priorizados para limpieza.
- [x] Smoke baseline y precondición de build limpia definidos.
- [x] Comando de verificación reproducible registrado.

## 7) Siguiente paso (Fase 1)

Con baseline congelada, ejecutar la validación de línea de vida `1v1` usando la checklist de sesión:

- `docs/session_smoke_checklist_1v1.md`
