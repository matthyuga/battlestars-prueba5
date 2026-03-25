# Diseño técnico implementable — Sistema de puntos por slot para técnicas

## 1) Objetivo
Diseñar e implementar un sistema pre-combate donde cada **slot de unidad** (ej. `P1`, `P2`, `E1`, `E2`) tenga una bolsa de puntos para asignar **bonus** a técnicas ofensivas/defensivas, sin romper:
- el cálculo actual de costos de Reiatsu/Energía,
- la ejecución en 1v1 y 2v2,
- la compatibilidad con IA,
- la arquitectura preparada para escalar a más equipos.

---

## 2) Estado actual (repositorio)

### 2.1 Costos actuales (SSOT)
- `TECH_STATS` y `TECH_SCALE` existen globalmente por técnica.
- Reiatsu se calcula 1:1 con `value`.
- Energía escala por casillas/bloques según `scale`.
- `reiatsu_energy_dynamic_cost` es la función de costo final usada por ejecución.

### 2.2 Modelo actual de unidades/slots
- Ya existe clave de unidad dinámica: `team:slot` (ej. `player:0`, `enemy:1`).
- Ya hay helpers para parsear, resolver y consumir recursos por unidad.
- En 2v2 se consume por unidad activa vía `bs_consume_unit_resources`.

### 2.3 Riesgo estructural hoy
- `TECH_STATS` es global por técnica: si se cambia allí, afecta a todos.
- Para personalización por slot, no debemos mutar `TECH_STATS`; debemos aplicar un **overlay por slot**.

---

## 3) Principios de diseño
1. **No romper SSOT**: mantener `reiatsu_energy_dynamic_cost` como punto central de costos.
2. **Base + Bonus**:
   - `base_value` sigue siendo la actual (100 inicial o balance global).
   - `bonus_points` es por slot y técnica.
3. **Per-slot, no global**: toda asignación vive en `unit_key` (`player:0`, etc.).
4. **Clamps estrictos**:
   - `bonus >= 0`
   - `spent <= available`
   - `bonus <= max_bonus_per_tech`
5. **Primero 1v1/2v2** con estructura extensible (equipos/slots dinámicos).

---

## 4) Modelo de datos propuesto

Crear estado persistente en `store`:

```python
battle_point_alloc = {
  "version": 1,
  "defaults": {
    "available_points_per_slot": 2000,
    "max_bonus_per_tech": 1000,
    "enabled": True,
  },
  "slots": {
    "player:0": {
      "available": 2000,
      "spent": 900,
      "remaining": 1100,
      "tech_bonus": {
        "direct_attack": 800,
        "defense_extra": 100
      },
      "updated_at": "..."
    },
    "enemy:0": { ... }
  }
}
```

Notas:
- `spent` y `remaining` pueden recalcularse siempre (evita drift), pero se guardan para UI rápida.
- `tech_bonus` solo guarda bonus explícitos (`0` puede omitirse).

---

## 5) API nueva (implementable)

Archivo sugerido: `game/04Y_SLOT_POINT_ALLOCATOR_V1.rpy`

### 5.1 Inicialización / sync
- `spa_ensure_state()`
- `spa_ensure_slot(unit_key)`
- `spa_reset_slot(unit_key)`
- `spa_reset_all()`

### 5.2 Lectura
- `spa_get_available(unit_key)`
- `spa_get_spent(unit_key)`
- `spa_get_remaining(unit_key)`
- `spa_get_bonus(unit_key, tech_id)`

### 5.3 Escritura segura
- `spa_set_bonus(unit_key, tech_id, new_bonus)`
- `spa_add_bonus(unit_key, tech_id, delta)`
- `spa_sub_bonus(unit_key, tech_id, delta)`

Retorno estándar sugerido:
```python
{
  "ok": True/False,
  "reason": "over_budget|invalid_tech|...",
  "before": {...},
  "after": {...}
}
```

### 5.4 Cálculo de poder final por slot
- `spa_get_base_value(tech_id)`  -> lee base desde `TECH_STATS`/`reiatsu_energy_base`
- `spa_get_final_value(unit_key, tech_id)` -> `base + bonus`

---

## 6) Integración con costos (sin romper flujo actual)

## 6.1 Cambio mínimo recomendado
Extender `reiatsu_energy_dynamic_cost(tech_id, user, **kwargs)` para aceptar:
- `unit_key=None` (opcional)

Nuevo comportamiento:
1. calcular `base_info` como hoy,
2. si `unit_key` existe y allocator habilitado: `value_final = base_value + bonus(unit_key, tech_id)`,
3. aplicar multiplicadores de focus/boost como hoy,
4. reiatsu final = `value_final * mult`,
5. energía = `calc_energy(value_final, scale)` (o mantener política actual si decides energía no-focus).

Esto mantiene una sola vía de costo para:
- selector,
- ejecución player,
- ejecución enemy,
- IA.

## 6.2 Compatibilidad
Si no llega `unit_key`, el comportamiento debe ser idéntico al actual.

---

## 7) Integración por capas del juego

## 7.1 Selector/UI pre-combate
Archivos candidatos:
- `game/04A_BATTLE_CHARACTER_SELECTV3.rpy` (entry flow)
- Nuevo screen: `game/04H_PREBATTLE_POINT_ALLOC_SCREENV1.rpy`

Flujo:
1. Selección de modo/equipo como hoy.
2. Antes de `battle_start`, abrir panel de puntos.
3. Usuario elige slot (`P1/P2/E1/E2`) y distribuye bonus.
4. Guardar en `battle_point_alloc`.

Controles de UX v1:
- botones `+10 +50 +100 -10 -50 -100`
- input manual con parse+clamp
- reset técnica
- reset slot
- indicador `Gastado/Disponible/Restante`
- preview de `Total`, `Reiatsu`, `Energía` por técnica

## 7.2 Selector de acciones en combate (preview)
Archivos candidatos:
- `game/04F_SELECTOR_MENUV2.rpy`
- `game/04F_SELECTOR_QUEUV2.rpy`
- `game/04F_SELECTOR_FUNCTIONS` (si aplica en tu rama)

Asegurar que `get_real_cost(...)` o equivalente inyecte `unit_key` del actor actual al pedir costo dinámico.

## 7.3 Ejecución real de acciones
Archivos candidatos:
- `game/4/04D_AI_EXECUTIONV5.rpy`
- `game/4/j/04C_OFFENSIVE_COREV3.rpy`
- `game/4/j/04D_DEFENSIVE_CORE.rpy`

Donde hoy se llama `reiatsu_energy_dynamic_cost(tech_id, S)`, pasar también `unit_key`:
- player: `bs_unit_key("player", owner_slot)`
- enemy: `bs_unit_key("enemy", owner_slot)`

## 7.4 IA (configuración de puntos)
V1:
- IA usa mismo allocator; asignación inicial por perfil simple (`aggressive/defensive/balanced`) en pre-combate.
- No requiere UI manual de IA para salir en primera fase.

V2:
- panel manual para E1/E2 + presets.

---

## 8) Validaciones obligatorias

## 8.1 Input/seguridad
- Parse seguro de entero (`try int`, fallback 0).
- Clamp min 0.
- Clamp max técnico (`MAX_BONUS_PER_TECH`, ej. 99999).
- Rechazar asignación que excede bolsa de slot.

## 8.2 Consistencia de cálculo
- Preview == costo consumido en ejecución.
- Misma técnica + mismo slot + mismo estado => mismo costo.

## 8.3 No regresión
- Si allocator deshabilitado, combate se comporta igual que hoy.

---

## 9) Plan por fases (implementación real)

## Fase 0 — Preparación (rápida)
- Añadir flags/config defaults (`available_points_per_slot`, `max_bonus_per_tech`, `enabled`).
- Añadir utilidades de log/debug para allocator.

Entregable: estado inicial estable, sin impacto funcional.

## Fase 1 — Core allocator (sin UI)
- Crear `04Y_SLOT_POINT_ALLOCATOR_V1.rpy` con API completa.
- Unit test manual por script/repl Ren'Py (set/add/sub/reset).

Entregable: overlay por slot funcionando en memoria/store.

## Fase 2 — Integrar costo dinámico
- Extender `reiatsu_energy_dynamic_cost` para `unit_key`.
- Mantener backward compatibility total.
- Integrar llamadas de ejecución player/enemy con `unit_key`.

Entregable: costos reales per-slot ya impactan combate.

## Fase 3 — Integrar preview selector
- Hacer que preview consulte costo con `unit_key` correcto.
- Validar que costo mostrado == costo consumido.

Entregable: UX coherente.

## Fase 4 — Pantalla pre-combate v1
- Slot picker + edición bonus por técnica.
- Botones de incremento + input manual seguro + reset.

Entregable: feature usable end-to-end.

## Fase 5 — IA perfiles + presets (opcional)
- Asignación automática por perfil.
- (Opcional) guardar/cargar presets por slot/personaje.

Entregable: mejora de diseño/balance.

---

## 10) Criterios de aceptación por fase

### Fase 1
- `spa_set_bonus("player:0", "direct_attack", 300)` deja bonus en 300.
- `remaining = available - spent` correcto.
- No permite negativos ni pasarse de presupuesto.

### Fase 2
- Con bonus 800 en técnica base 100:
  - valor final = 900,
  - reiatsu = 900 (sin focus),
  - energía corresponde a escala de esa técnica.

### Fase 3
- Preview muestra exactamente esos costos y ejecución descuenta igual.

### Fase 4
- Usuario puede editar P1/P2/E1/E2 antes de combate.
- Reset por técnica/slot funciona.

---

## 11) Decisiones abiertas (para cerrar antes de codificar Fase 4)
1. ¿El `available_points_per_slot` será fijo, por nivel, o por modo?
2. ¿Habrá tope de bonus por técnica distinto por tipo (`offensive/defensive`)?
3. ¿`focus/boost` pueden recibir bonus? (recomendado: no, por ser especiales)
4. ¿IA en v1 usa reparto automático por perfil o espejo del player?

---

## 12) Recomendación de parámetros iniciales (v1)
- `available_points_per_slot = 2000`
- `max_bonus_per_tech = 1000`
- pasos UI: `10 / 50 / 100`
- técnicas especiales sin bonus

Estos valores permiten testear builds sin inflar demasiado la economía de recursos.

---

## 13) Resumen técnico
- Implementar un **overlay de puntos por slot** (no tocar `TECH_STATS` global).
- Inyectar `unit_key` en el cálculo dinámico ya existente.
- Integrar primero ejecución y preview, luego UI pre-combate.
- Mantener compatibilidad 1v1/2v2 hoy, listo para escalar a más equipos mañana.
