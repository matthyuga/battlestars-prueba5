# Diagnóstico del Facade mínimo y próximos pasos

## Estado actual (respecto al objetivo original)

### 1) HP centralizado
**Estado: avanzado (parcialmente adoptado).**

- Ya existe `battle_state` con `units.player/enemy.hp` y `max_hp`, inicialización segura y clamps.
- Ya existen helpers `bs_hp`, `bs_max_hp`, `bs_set_hp`, `bs_set_max_hp`, `bs_apply_damage`, y sincronización bidireccional con variables legacy (`player_hp`, `enemy_hp`, `battle_hp_*`).
- Esto permite migración progresiva sin romper módulos antiguos.

**Qué falta:**
- Adoptar `bs_apply_damage`/`bs_set_hp` como ruta principal en todos los labels críticos para evitar escrituras directas mezcladas.
- Reducir gradualmente escrituras directas a `player_hp/enemy_hp` fuera del facade.

### 2) Reflect centralizado
**Estado: sólido a nivel de manager + helpers.**

- `ReflectManager` centraliza reflect por `target` y guarda `source`.
- Hay API moderna (`consume_info`) y compat legacy (`consume`).
- Existen helpers `reflect_queue/consume_for/peek_for/clear_for` para desacoplar al resto del código del manager interno.

**Qué falta:**
- Endurecer regla de uso: que módulos de combate no llamen directamente `reflect.add/consume`, sino solo helpers.
- Definir una política única de “cuándo expira reflect” por fase/turno (ahora hay ramas que consumen o desvanecen según flujo).

### 3) Turn owner único
**Estado: incompleto (conviven 2 sistemas).**

- Existe `battle_turn_owner` (usado en inicio/flujo de turnos).
- También existe `battle_actor + battle_phase + battle_turn_no` con helpers (`battle_next_phase`).

**Riesgo principal:**
- Tener dos fuentes de verdad para turno puede generar desincronizaciones difíciles de depurar.

**Qué falta:**
- Crear facade de turno (`bs_get_turn_owner`, `bs_set_turn_owner`, `bs_advance_turn`) y usarlo como única puerta de entrada.
- Mantener espejo temporal de compatibilidad durante migración (dual-write controlado).

---

## Diagnóstico general

Vienen bien: ya tienen una **base real de facade para HP** y una **columna fuerte para reflect**. El punto más frágil hoy es el **turn ownership duplicado**. Si corrigen eso primero, el resto de la reestructuración queda mucho más prolija.

---

## Camino recomendado (sin romper nada)

## Fase 1 — Consolidación del facade mínimo
1. Congelar API pública mínima:
   - HP: `bs_hp`, `bs_set_hp`, `bs_apply_damage`, `bs_sync_to_legacy`.
   - Reflect: `reflect_queue`, `reflect_consume_for`, `reflect_peek_for`.
   - Turno: `bs_get_turn_owner`, `bs_set_turn_owner`, `bs_advance_turn` (nuevo).
2. Marcar como deprecated las escrituras directas a `player_hp/enemy_hp` en módulos de combate.
3. Añadir logging de auditoría en modo debug para detectar bypass al facade.

## Fase 2 — Battle state unificado por unidades (pre-2v2)
Estructura sugerida:

```python
battle_state = {
  "version": 2,
  "turn": {
    "owner_team": "player",
    "owner_slot": 0,
    "phase": "offensive",
    "round": 1,
  },
  "teams": {
    "player": [{"id": "Ichigo", "hp": 120, "max_hp": 120, "stats": {...}}, ...],
    "enemy":  [{"id": "Hollow", "hp": 100, "max_hp": 100, "stats": {...}}, ...],
  },
  "effects": {
    "reflect": {"target_key": {"value": 20, "source_key": "enemy:0"}}
  }
}
```

Con esto, pasar de 1v1 a 2v2/5v5 es escalar listas y selector de objetivo, no reescribir todo.

## Fase 3 — Sistema de stats + ítems
1. Separar stats base y derivadas:
   - Base: fuerza, agilidad, inteligencia.
   - Derivadas: ataque, defensa, reiatsu, energía, hp_max.
2. Pipeline único de cálculo:
   - `base + crecimiento + equipo + buffs/debuffs = final`.
3. Ítems como modificadores declarativos (no hardcode por técnica):
   - `{"str": +3, "agi": +1, "energy_max": +10}`.
4. Recalcular derivadas en hooks bien definidos:
   - inicio de combate,
   - equip/unequip,
   - aplicación/expiración de buff.

---

## Priorización práctica (orden de implementación)

1. **Unificar turno** (alto impacto, bajo costo técnico).
2. **Cerrar bypass de HP/Reflect** (consistencia).
3. **Modelar unidades por equipo** (habilita 2v2→5v5).
4. **Introducir stats base/derivadas**.
5. **Agregar inventario/ítems**.

---

## Criterios de “repo prolijo” para próximas actualizaciones

- Un solo módulo facade como contrato de estado (`battle_state` + turn + reflect).
- Módulos de combate sin escrituras directas a globals críticas.
- Compat legacy encapsulada en una sola capa (`sync_to_legacy` / `sync_from_legacy`).
- Tests de humo por flujo (`player start`, `enemy start`, KO con reflect, cambio de turno).
- Versionado interno de `battle_state` para migraciones de saves.

---

## Conclusión

Sí: **ya hicieron avances reales en la dirección correcta** (HP facade + reflect moderno).

No: **todavía no está cerrado el objetivo mínimo completo** porque falta consolidar **turn owner** como SSOT y completar adopción en labels críticos.

Si siguen el camino por fases (primero turno, luego equipos/unidades, luego stats/ítems), el salto a 2v2–5v5 se vuelve incremental y seguro.
