# Phase 11 — Reconstrucción + Hand-off histórico (ayer/hoy)

> Objetivo: dejar una bitácora única de lo reconstruido, qué funcionó, qué rompimos en el camino y qué NO repetir en próximas sesiones.

## 1) Resumen ejecutivo

Durante estas dos jornadas se completó una reestructuración grande del sistema de turnos:

- **Contrato público estable** para labels de turno (fachada) y routers por modo (`1v1` / `2v2`).
- **Aislamiento de contexto entrante 2v2 (SSOT)** para reducir contaminación entre slots/turnos.
- **Gateway UI runtime-safe** para concentrar `show/hide/pause/restart` y evitar llamadas dispersas.
- **Higiene de popups** (distinguir popup de turno vs ventana de maniobras).
- **Instrumentación en transición enemy -> defensive** para depurar por slot/target en 2v2.

Resultado actual reportado por QA manual: base estable, con fixes aplicados para los puntos críticos detectados.

---

## 2) Línea de tiempo (ayer -> hoy)

## Fase de reconstrucción (base técnica)

- Se alineó la base y se conservaron docs de migración (`reset` de referencia).
- Se hizo hardening incremental del flujo defensivo y visuales:
  - fallback seguro para `pause/with_statement`,
  - guardas de `get_screen` / `restart_interaction`,
  - normalización de codificación UTF-8 sin BOM,
  - limpieza de errores de parse/indent.

## Reestructuración de routing y contrato

- Se consolidó la fachada pública con adapter + contrato de rutas.
- Se separaron routers `1v1` y `2v2`.
- Se removieron wrappers legacy duplicados en puntos de entrada para evitar ambigüedad.
- Se añadieron trazas de ruta unificadas para auditoría (`ROUTE ...`).

## Reestructuración de popup/maniobras y 2v2

- Se separó explícitamente concepto A vs B:
  - **A**: popup de turno (`battle_popup_turn`).
  - **B**: ventana de maniobras/daño entrante (`battle_maneuver_choice`).
- Se instrumentó transición enemy->defensive en 2v2 (attempt/result/slot/target/branch).
- Se corrigió el flujo diferido de daño entrante en 2v2 para volver a mostrar la ventana de maniobras.

---

## 3) Pasos en falso (importante para no repetir)

## Error A — Crash de arranque por API Ren'Py “pisada”

### Síntoma
Crash temprano en `gui/layout` con errores tipo:

- `AttributeError: module object has no attribute has_screen`
- luego también `... no attribute pure`

### Causa raíz
En bloques `init python` se usó `import renpy` en lugares sensibles.
Eso puede **sombrear** el objeto API de Ren'Py del store con el módulo Python, dejando fuera atributos esperados por scripts comunes.

### Corrección aplicada
- Evitar `import renpy` en esos bloques.
- Usar referencia store-safe (`_renpy_api = renpy`) y operar sobre esa referencia.
- Shim mínimo de compatibilidad en bootstrap para APIs críticas tempranas.

### Regla futura
> En `init python` del juego, **no** importar `renpy` directo salvo necesidad extrema; preferir `renpy.store as S` y/o alias store-safe local.

---

## Error B — “Screen battle_popup_turn is not known”

### Síntoma
El juego avanzaba, pero al mostrar popup de turno en runtime lanzaba:

- `Exception: Screen battle_popup_turn is not known.`

### Causa raíz
Combinación de factores de carga/descubrimiento del script del popup durante cambios de nombre/codificación.

### Corrección aplicada
- Se canonizó el archivo del popup de turno (`06D_BATTLE_POPUP_TURN.rpy`) y se normalizó codificación.
- Se endureció `bs_ui_show(...)` para fallar de forma segura + log en vez de abortar flujo.

### Regla futura
> Evitar cambios de casing/extensión ambiguos y BOM en archivos `.rpy` de screens críticos.

---

## Error C — “could not find label 'battle_enemy_turn'” al quitar scripts

### Síntoma
Al remover archivos de la nueva capa de routing para “probar”, el runtime no encontró labels públicos.

### Causa raíz
Los labels públicos quedaron delegados a guard/adapter/router; al quitar piezas de esa cadena se rompen saltos.

### Corrección aplicada
Se restauró la cadena completa pública -> adapter -> router -> impl/legacy.

### Regla futura
> No borrar parcialmente la capa de routing nueva; si se desactiva algo, hacerlo completo y de forma controlada.

---

## Error D — 2v2 sin ventana de daño entrante (maniobras)

### Síntoma
En 2v2 se veía la transición de turno pero no aparecía `battle_maneuver_choice`.

### Causa raíz
En el flujo diferido de daño entrante (ofensivo 2v2), el código hacía salto directo a `battle_defensive_turn` y **saltaba la ventana**.

### Corrección aplicada
Se reinstaló el bloque de:

- feedback visual de daño,
- `show battle_maneuver_choice`,
- espera de `maneuver_selected`,
- bifurcación por maniobra.

### Regla futura
> Cualquier rama con daño entrante 2v2 debe pasar por el mismo contrato de maniobras antes del salto final.

---

## Error E — `def_from_atk` con semántica incompleta

### Síntoma
`atk_from_def` sí otorgaba acción extra; `def_from_atk` no estaba espejo: no sumaba extra defensiva y acababa en ofensivo.

### Causa raíz
Faltaba branch explícito para `def_from_atk` en la rama diferida 2v2.

### Corrección aplicada
Para `def_from_atk` ahora:

- activa `defense_for_attack_active`,
- limpia extra ofensiva,
- suma `extra_defensive_actions += 1`,
- limpia flags de retorno diferido ofensivo,
- salta a `battle_defensive_turn`.

### Regla futura
> Mantener tabla de simetría de maniobras (beneficio/costo/turno destino) y validarla en cada branch.

---

## 4) Estado actual (foto para próxima sesión)

- Routing público y separación por modo: **activo**.
- Contrato + trazas de ruta: **activo**.
- Popup de turno (A) vs ventana de maniobras (B): **separación explícita aplicada**.
- Instrumentación 2v2 en transición enemy->defensive: **activa**.
- Ventana de daño entrante 2v2: **restaurada**.
- Semántica `def_from_atk` (acción defensiva extra): **ajustada**.

---

## 5) Checklist de seguridad para próximas modificaciones

Antes de tocar flujo de turnos:

1. Ejecutar higiene de build (`qa_clean_build.sh`) para evitar artefactos viejos.
2. Confirmar que existe una sola implementación canónica para cada screen crítico.
3. No introducir `import renpy` en `init python` donde pueda pisar API store.
4. Si se toca 2v2 diferido, validar ambos branches:
   - `atk_from_def`
   - `def_from_atk`
5. Smoke mínimo recomendado:
   - 1v1 completo,
   - 2v2 slot 0,
   - 2v2 slot 1,
   - transición enemy->defensive con logs.

---

## 6) Nota operativa

Si aparece un comportamiento “inexplicable”, primero descartar:

- `.rpyc/.rpymc` stale,
- archivos con BOM,
- rutas parcialmente removidas (guard/adapter/router),
- screens duplicadas con naming ambiguo.

