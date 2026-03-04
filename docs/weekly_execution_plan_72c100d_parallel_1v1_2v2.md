# Plan semanal de ejecución (baseline `72c100d`)

## Objetivo
Recuperar y estabilizar flujo de combate separando `1v1` y `2v2` sin perder paralelismo estructural:

- `1v1`: target automático (jugador vs IA).
- `2v2`: target explícito (slot 0/1).

La estrategia es mantener un **core compartido** de resolución y dos rutas de orquestación separadas por modo.

---

## Decisión de arquitectura (primero reestructurar mínimo, luego fixes)

1. **No seguir con parches aislados sobre labels críticos.**
2. **Crear partición por modo** (`1v1` / `2v2`) en la capa de turno/ruteo.
3. **Mantener core compartido** para evitar divergencia funcional.
4. **Reintegrar defensivo después de estabilizar contrato + runtime-safe wrappers.**

---

## Estructura propuesta de scripts (registrada para implementación)

> Estos archivos pueden crearse gradualmente. Si alguno no se crea en una iteración, mantener la ruta en este documento para trazabilidad.

### Núcleo compartido (sin UI)
- `game/4/core/battle_turn_contract.rpy`
- `game/4/core/battle_targeting_shared.rpy`
- `game/4/core/battle_damage_pipeline_shared.rpy`

### Orquestación 1v1
- `game/4/modes/1v1/battle_router_1v1.rpy`
- `game/4/modes/1v1/battle_defensive_1v1.rpy`

### Orquestación 2v2
- `game/4/modes/2v2/battle_router_2v2.rpy`
- `game/4/modes/2v2/battle_defensive_2v2.rpy`
- `game/4/modes/2v2/battle_incoming_ctx_2v2.rpy`

### Compat/UI gateway (único)
- `game/4/shared/battle_runtime_ui_gateway.rpy`

---

## Backlog ejecutable (10 tareas, 1 semana)

## Día 1 — Contrato y observabilidad

### T1. Congelar contrato de labels públicas
**Cambio:** declarar y documentar entradas únicas:
- `battle_offensive_turn`
- `battle_enemy_turn`
- `battle_defensive_turn`

**Archivos foco:**
- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
- `game/4/j/04C_OFFENSIVE_COREV3.rpy`
- `game/4/j/04D_DEFENSIVE_CORE.rpy`
- `game/4/core/battle_turn_contract.rpy` (nuevo)

**Criterio de prueba:** cada entrada pública resuelve una sola ruta por modo (sin duplicados legacy activos).

### T2. Instrumentación mínima de rutas (debug)
**Cambio:** logging controlado por flag (`battle_debug_routes`) con formato:
`ROUTE mode=<1v1|2v2> phase=<off|enemy|def> owner=<unit> target=<slot|auto>`

**Criterio de prueba:** en combate se observa la secuencia completa sin saltos ambiguos.

---

## Día 2 — Runtime-safe y error de 25 s

### T3. Unificar gateway UI-safe
**Cambio:** centralizar `show/hide/get/restart/pause/with/random/has_label` en:
- `game/4/shared/battle_runtime_ui_gateway.rpy` (nuevo)

**Criterio de prueba:** en módulos críticos no quedan llamadas directas `renpy.*` fuera del gateway.

### T4. Mitigar error "después de 25 s"
**Cambio:** agregar trazas con timestamp por fase y guardas para detectar estancamiento en transición `enemy -> defensive`.

**Regla:** si no se cumple precondición de defensivo, fallback controlado a ruta segura con log explícito, nunca freeze silencioso.

**Criterio de prueba:** cuando se reproduce el caso, queda log de causa y la sesión no queda bloqueada.

---

## Día 3 — Separación 1v1 sin romper estabilidad

### T5. Router 1v1 dedicado
**Cambio:** encapsular target automático y transición defensiva 1v1 en:
- `game/4/modes/1v1/battle_router_1v1.rpy` (nuevo)

**Criterio de prueba:** smoke 1v1 completo (ataque enemigo -> popup -> defensivo -> resolución) estable.

### T6. Defensivo 1v1 dedicado
**Cambio:** mover lógica específica de defensor único a:
- `game/4/modes/1v1/battle_defensive_1v1.rpy` (nuevo)

**Criterio de prueba:** cero dependencia de `incoming_ctx` o estructura por slots de 2v2 en 1v1.

---

## Día 4 — Separación 2v2 con paralelismo

### T7. Router 2v2 dedicado
**Cambio:** implementar selección de target explícito (slot 0/1) en:
- `game/4/modes/2v2/battle_router_2v2.rpy` (nuevo)

**Criterio de prueba:** el target elegido coincide con defensor/popup/hud en secuencia.

### T8. Contexto de daño entrante 2v2
**Cambio:** aislar manejo de contexto entrante en:
- `game/4/modes/2v2/battle_incoming_ctx_2v2.rpy` (nuevo)

**Criterio de prueba:** no hay contaminación de contexto entre ataques consecutivos ni entre unidades.

---

## Día 5 — Reintegración y limpieza controlada

### T9. Adapter de contrato (router público -> routers por modo)
**Cambio:** mantener labels públicas como fachada estable y delegar internamente a `1v1` o `2v2`.

**Criterio de prueba:** llamadas externas no cambian; internamente existe SSOT por modo.

### T10. Limpieza de rutas legacy duplicadas
**Cambio:** retirar rutas/guards redundantes de turno defensivo que compitan con el router activo.

**Criterio de prueba:** no hay más de una ruta efectiva por fase y modo.

---

## Matriz de validación por iteración

1. `1v1` normal (target automático).
2. `1v1` desde transición ofensiva->defensiva (`def_from_atk`).
3. `2v2` target slot 0.
4. `2v2` target slot 1.
5. Ruta `skip/no_damage`.
6. Repetición de combate para verificar que no queden estados sucios.

> Antes de cada smoke importante: limpiar caché/compilados para evitar falsos positivos por `.rpyc` desalineados.

---

## Criterio de éxito semanal (Go/No-Go)

### Go
- `1v1` estable sin freeze/crash en transición defensiva.
- `2v2` respeta target explícito y coherencia popup/defensor/HUD.
- Router público único con delegación limpia por modo.

### No-Go
- Traceback apunta a líneas inexistentes (build/caché desalineado).
- Existen rutas duplicadas activas en defensivo.
- Persisten bloqueos sin logging causal.

---

## Política de commits recomendada

- Commits pequeños por tarea (T1..T10).
- Mensajes con prefijo:
  - `battle-contract:`
  - `battle-ui-gateway:`
  - `battle-1v1:`
  - `battle-2v2:`
  - `battle-cleanup:`
- Cada commit debe incluir evidencia de smoke mínimo ejecutado.
