# Plan maestro de limpieza y reestructuración (post-migración 2v2)

## Contexto y objetivo

El repositorio acumuló capas de compatibilidad, fallbacks y rutas legacy durante la migración `1v1 -> 2v2`.
El objetivo de este plan es **reducir complejidad accidental** y volver el flujo de combate
predecible, testeable y mantenible.

Este plan sigue 5 líneas de trabajo:

1. Congelar `1v1` estable en un módulo limpio.
2. Separar `2v2` en namespace propio.
3. Eliminar rutas legacy no usadas y dejar una sola entrada pública por turno.
4. Unificar API UI en una sola capa.
5. Limpiar/reconstruir cache/build para evitar desalineación entre fuente y runtime.

---

## Principios de ejecución

- **No romper comportamiento de jugador**: cada fase debe mantener jugabilidad base.
- **Cambios pequeños y verificables**: una fase por PR cuando sea posible.
- **Observabilidad obligatoria**: logs mínimos de ruta activa por turno y modo.
- **Sin “parches encima de parches”**: si una ruta queda obsoleta, se elimina.
- **Fuente de verdad única por concern**:
  - routing de turnos,
  - estado de daño entrante,
  - capa UI runtime-safe.

---

## Fase 0 — Inventario y congelamiento de baseline

### Objetivo
Tener una foto técnica clara y una baseline reproducible antes de limpiar.

### Tareas
- Congelar snapshot de labels públicas y rutas actuales de turno.
- Listar archivos con alta densidad de `legacy/fallback/compat`.
- Registrar mapa de dependencias críticas:
  - `battle_*_turn`
  - `battle_popup_turn`
  - `battle_command_menu`
  - wrappers UI (`ui_*_safe`, `ensure_renpy_ui_apis`).
- Definir escenario smoke mínimo obligatorio:
  - 1v1: ataque enemigo -> turno defensivo -> resolución.
  - 2v2: daño diferido a slot y entrada defensiva del slot correcto.

### Criterio de salida
Existe documento de inventario y smoke baseline ejecutable por cualquier dev.

---

## Fase 1 — Congelar 1v1 estable (línea de vida)

### Objetivo
Aislar un camino `1v1` limpio y estable sin dependencia accidental de lógica `2v2`.

### Tareas
- Crear módulo explícito `legacy_1v1` para flujo de turnos (ofensivo/enemigo/defensivo).
- Mover/encapsular helpers estrictamente 1v1 fuera de rutas compartidas.
- Asegurar que `battle_team_mode == 1v1` no use colas/per-unit maps de 2v2.
- Mantener logs de trazabilidad:
  - `ROUTE mode=1v1 owner=... label=...`

### Criterio de salida
1v1 corre completo sin tocar rutas de 2v2 ni banderas de migración.

---

## Fase 2 — Namespace propio para 2v2

### Objetivo
Evitar contaminación cruzada entre 1v1 y 2v2.

### Tareas
- Reubicar/renombrar entrypoints 2v2 bajo namespace claro (`*_2v2_*`).
- Agrupar estado 2v2 en estructura dedicada (incoming/deferred/slot context).
- Eliminar acoplamientos implícitos entre `battle_player/enemy` legacy y unidades 2v2.
- Definir adaptador explícito donde se necesite compat legacy.

### Criterio de salida
El flujo 2v2 se puede seguir de punta a punta sin depender de estado legacy ambiguo.

---

## Fase 3 — Racionalización de labels y router único

### Objetivo
Tener una sola puerta de entrada pública por turno.

### Tareas
- Mantener únicamente labels públicas:
  - `battle_offensive_turn`
  - `battle_enemy_turn`
  - `battle_defensive_turn`
- Redirigir internamente a implementaciones concretas por modo.
- Eliminar labels duplicadas/obsoletas y guards redundantes.
- Añadir verificación de consistencia en arranque (debug):
  - resolver target final por label pública y loguearlo.

### Criterio de salida
No hay ambigüedad de resolución de labels ni rutas solapadas.

---

## Fase 4 — Unificación total de capa UI runtime-safe

### Objetivo
Todo acceso UI pasa por un único gateway seguro.

### Tareas
- Crear API canónica única (ejemplo):
  - `ui_show(name, **kwargs)`
  - `ui_hide(name)`
  - `ui_get(name)`
  - `ui_restart()`
- Reemplazar llamadas directas dispersas a `renpy.show_screen/hide_screen/get_screen/restart_interaction`.
- Convertir wrappers antiguos a aliases temporales y luego retirarlos.
- Mantener fallback no-op únicamente en el gateway central.

### Criterio de salida
No quedan llamadas directas a UI fuera del gateway acordado (excepto gateway mismo).

---

## Fase 5 — Limpieza final de compat y deudas técnicas

### Objetivo
Reducir superficie de bugs heredados.

### Tareas
- Eliminar flags/variables transitorias sin uso real.
- Consolidar logs debug redundantes.
- Remover rutas fallback que ya no se usan.
- Revisar docs para reflejar arquitectura final.

### Criterio de salida
Disminuye significativamente el código `legacy/fallback/compat` y se simplifica onboarding.

---

## Fase 6 — Build hygiene y validación de distribución

### Objetivo
Asegurar que runtime ejecuta exactamente el código fuente vigente.

### Tareas
- Definir rutina oficial de limpieza antes de QA:
  - limpiar cachés/compilados del proyecto,
  - rebuild completo,
  - smoke tests sobre build limpia.
- Registrar hash/versión de build probado y fecha.
- Verificar que traceback de QA mapee líneas reales del repo.

### Criterio de salida
No hay desalineación entre fuente y runtime en pruebas manuales.

---

## Matriz de riesgos

- **Riesgo:** romper flujo 1v1 al limpiar 2v2.  
  **Mitigación:** fase 1 primero + smoke 1v1 obligatorio en cada PR.

- **Riesgo:** eliminar fallback aún necesario en runtime específico.  
  **Mitigación:** gateway UI único con fallback controlado y logging.

- **Riesgo:** sesiones QA usando build stale.  
  **Mitigación:** fase 6 obligatoria antes de validar regresiones.

---

## Checklist operativo por PR

- [ ] Cambios limitados a una fase concreta.
- [ ] Logs de ruta activa revisados.
- [ ] Smoke 1v1 ejecutado.
- [ ] Smoke 2v2 ejecutado (si aplica).
- [ ] Documentación de fase actualizada.
- [ ] Confirmación de build limpia/caché limpia para QA.

---

## Propuesta de orden real (recomendado)

1. Fase 0 (inventario + baseline).  
2. Fase 1 (blindar 1v1).  
3. Fase 3 (router único, quitar ambigüedad).  
4. Fase 4 (gateway UI único).  
5. Fase 2 (aislar 2v2 ya con base limpia).  
6. Fase 5 (remoción de deuda).  
7. Fase 6 (higiene build y validación final).

> Nota: este orden prioriza estabilidad inmediata del flujo defensivo (1v1/entrypoints/UI)
> antes de seguir expandiendo la migración 2v2.
