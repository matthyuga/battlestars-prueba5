# Mapa de reestructuración/migración por fases (rango `eb6af1b` → `df14ab0`)

## 1) Veredicto ejecutivo

- En el rango 1..55 hay **dos problemas superpuestos**:
  1. regresión funcional del flujo ofensivo IA → defensivo (disparada desde `324d556`),
  2. deuda previa de compatibilidad runtime (`renpy.*`) ya presente antes del commit 9.
- Por eso mezclar scripts de distintos commits rompe contratos (labels/router) y activa crashes de API faltante.

## 2) Lectura del rango 1..55 por bloques

### Bloque A — Base funcional 2v2 previa (1..9)
- Desde `eb6af1b` hasta `72c100d` se concentran ajustes de lógica 2v2/defensa diferida sin introducir aún la capa fuerte de router+compat global.
- `72c100d` es el último punto que reportaste como jugable sin crash de defensivo (aunque con deuda en aviso entrante).

### Bloque B — Inicio de regresión en transición entrante/defensivo (10..21)
- En `324d556` entra el cambio de visibilidad de aviso entrante en el flujo enemigo.
- Entre `948090c` y `50e996d` se encadena migración C1..C4 + fixes de routing/ctx/popup (mucha superficie cambiada a la vez).

### Bloque C — Hardening y mitigaciones de runtime (22..55)
- Desde `6c2827f` en adelante aparecen commits explícitos para APIs faltantes y hardening (`get_screen`, `pause`, `with_statement`, `random`, BOM/encoding, etc.).
- Este bloque mejora robustez, pero también evidencia que la base ya venía frágil por API/runtime mixto.

## 3) Scripts comprometidos (alto riesgo)

> Criterio: alto churn en 1..55 + alta densidad de llamadas directas `renpy.*` + rol crítico en turnos.

1. `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
   - Churn muy alto en rango (15 cambios) y muchas rutas críticas (header IA, transición entrante, salto a defensivo).
   - Es el principal “epicentro” de regresión funcional.

2. `game/4/j/04C_OFFENSIVE_COREV3.rpy`
   - Churn alto (15) y alta densidad de UI/pausas/saltos directos.
   - Acopla popup, salto de turno y lógica de acciones.

3. `game/4/j/04D_DEFENSIVE_CORE.rpy`
   - Churn más alto del rango (18).
   - Mezcla lógica de target/ctx + pantalla/espera + routing defensivo.

4. `game/04a_battle_fallbacks_fxV2.rpy` y `game/00_GLOBALS_SYSTEMV3.rpy`
   - Churn alto (12+12) en capa de compatibilidad.
   - Son infraestructura compartida: cualquier desalineación impacta todo el combate.

5. `game/06A_BATTLE_HUD_SYSTEMV2.rpy`, `game/03_VISUAL_SYSTEM_BASICV2.rpy`, `game/06B1_BATTLE_FX_CORE.rpy`
   - Zona de APIs sensibles (`get_screen`, `restart_interaction`, `random`, `pause`) y efectos visuales.

## 4) Scripts relativamente “a salvo” (mejor base lógica)

> Criterio: menor acoplamiento UI runtime + sin llamadas directas `renpy.*` sensibles en su núcleo.

- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy`
- `game/4/j/04D_DEFENSIVE_OPERATION.rpy`
- `game/4/04D_AI_REACTIVE_DEFENSE_ENGINEV2.rpy`
- `game/4/04D_AI_EXECUTIONV5.rpy`

Estos scripts son mejores candidatos para preservar/reusar al reiniciar migración, porque concentran más lógica de combate que plumbing UI.

## 5) Si hubiera que “volver a empezar”: base recomendada del 1..55

## Recomendación principal
Tomar **`72c100d` como base funcional** (dentro de 1..55) y rehacer migración en capas.

### Por qué `72c100d`
- Es el último punto del bloque temprano donde reportaste flujo jugable sin crash duro en defensivo.
- Evita arrastrar el pico de cambios encadenados del bloque C1..C4 iniciado en `324d556`.
- Permite reconstruir compatibilidad API de forma controlada, sin mezclar router/labels/popup de múltiples estados intermedios.

### Qué sí “rescatar” después (selectivo)
Aplicar de forma aislada (cherry-pick/manual) sólo hardenings de API que son acotados y de bajo riesgo funcional:
- `16e5f8c` (fallback seguro de `random` en FX),
- `b8549b3` (guard de phase log cuando falta `get_screen`),
- `60a9f6c` (guard de refresh/restart interaction),
- `39c7435` + `2e49da3` (UTF-8 sin BOM / parse).

No arrastrar en bloque los commits de router+popup+ctx sin consolidación, porque reintroducen dependencia cruzada de labels/rutas.

## 6) Plan por fases (propuesta concreta)

### Fase 0 — Congelamiento y contrato
- Congelar labels públicas: `battle_offensive_turn`, `battle_enemy_turn`, `battle_defensive_turn`.
- Definir un único punto de verdad para entrada de turno (sin duplicados guard/router/legacy en paralelo).

### Fase 1 — Compat API mínima obligatoria
- Centralizar wrappers runtime-safe para: `show_screen`, `hide_screen`, `get_screen`, `restart_interaction`, `pause`, `with_statement`, `random`, `has_label`.
- Prohibir llamadas directas `renpy.*` en scripts críticos de turno.

### Fase 2 — Aislar dominio de combate
- Mantener cálculo/estado en scripts “a salvo”.
- Mover presentación (popup/HUD/FX) a helpers invocados desde dominio (no inline en labels largas).

### Fase 3 — Reintegrar flujo enemigo→defensivo
- Reintroducir aviso “Daño entrante” con helper único.
- Validar 1v1 primero; luego 2v2 con `incoming_ctx` y target explícito.

### Fase 4 — QA incremental obligatoria
- Matriz mínima: 1v1 normal, 1v1 def_from_atk, 2v2 target slot 0/1, rutas con skip/no_damage.
- Build limpia/caché limpia en cada iteración para evitar falsos positivos de `.rpyc` legacy.

## 7) Regla operativa para evitar repetir el incidente

- No mezclar scripts sueltos de commits distintos en módulos de turno.
- Promover siempre “snapshot coherente por commit” + smoke corto por fase.
- Si aparece traceback con líneas que no existen en fuente actual, asumir desalineación de build antes de tocar lógica.
