# CONTRATO_TOWER_RUN_STATE_V1

Fecha: 2026-04-07  
Estado: Draft SSOT (Fase 5)

## 1) Objetivo

Definir el contrato canónico de estado de run para Torre del Cielo, incluyendo progreso, buffs temporales, personajes temporales y consolidación final.

---

## 2) Estructura canónica `tower_run_state`

Campos mínimos:
- `run_id` (string)
- `owner_id` (string)
- `season_id` (string opcional)
- `current_floor` (int)
- `current_block` (string: `C|B|A|S|...`)
- `active_buffs` (array)
- `temporary_characters` (array)
- `run_rewards_buffer` (objeto)
- `run_status` (enum): `active | completed | failed | abandoned`
- `started_at` (iso datetime)
- `updated_at` (iso datetime)

---

## 3) Tipos auxiliares

### 3.1 `tower_buff_entry`
- `buff_id`
- `buff_type`
- `value`
- `duration_kind` (`battle|run|floors`)
- `duration_remaining`

### 3.2 `temporary_character_entry`
- `character_id`
- `joined_at_floor`
- `is_temporary` (bool, default `true`)
- `conversion_rule_id` (opcional)
- `converted_to_permanent` (bool)

### 3.3 `run_rewards_buffer`
- `gold`
- `stars`
- `items[]`
- `tickets{C,B,A}`
- `characters[]`

---

## 4) Transiciones de estado

Permitidas:
1. `active -> completed`
2. `active -> failed`
3. `active -> abandoned`

No permitidas:
- cualquier transición desde `completed|failed|abandoned` a `active`.

---

## 5) Reglas de consolidación al cerrar run

Al cerrar run:
1. Persistir `run_rewards_buffer` al perfil global.
2. Limpiar `active_buffs` temporales de run.
3. Resolver personajes temporales:
   - si cumplen conversión: marcar permanentes.
   - si no: remover.
4. Emitir `tower_run_summary` auditable.

---

## 6) Estructura `tower_run_summary`

Campos mínimos:
- `run_id`
- `owner_id`
- `run_end_reason`
- `max_floor_reached`
- `floors_cleared`
- `rewards_granted`
- `temporary_characters_converted`
- `temporary_characters_removed`
- `closed_at`

---

## 7) Invariantes

1. `current_floor` nunca disminuye dentro de una run activa.
2. `run_status=active` requiere `started_at` definido.
3. `temporary_characters` no puede contener duplicados del mismo `character_id`.
4. Ninguna recompensa negativa en `run_rewards_buffer`.
5. Cierre de run debe producir exactamente un `tower_run_summary`.

---

## 8) Ejemplo JSON mínimo

```json
{
  "run_id": "TRUN-0001",
  "owner_id": "player_001",
  "current_floor": 12,
  "current_block": "C",
  "active_buffs": [],
  "temporary_characters": [],
  "run_rewards_buffer": {
    "gold": 320,
    "stars": 4,
    "items": [],
    "tickets": {"C": 0, "B": 0, "A": 0},
    "characters": []
  },
  "run_status": "active",
  "started_at": "2026-04-07T00:00:00Z",
  "updated_at": "2026-04-07T00:00:00Z"
}
```
