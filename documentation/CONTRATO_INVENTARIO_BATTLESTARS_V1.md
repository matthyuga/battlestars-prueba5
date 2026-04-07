# CONTRATO_INVENTARIO_BATTLESTARS_V1

Fecha: 2026-04-06  
Estado: Draft SSOT (Fase 0)

## 1) Objetivo

Definir el contrato canónico de inventario para que UI y runtime compartan la misma estructura de datos.

---

## 2) Entidades canónicas

### 2.1 `item_catalog`

Representa la definición estática de cada ítem.

Campos mínimos:
- `item_id` (string, único)
- `item_type` (enum): `consumable | equipable | amulet | tattoo`
- `subtype` (enum abierto):
  - consumibles: `hp_potion | ec_potion | ep_potion | durability_potion | atk_buff | def_buff | stat_buff`
  - equipables: `ring | necklace | circlet | bracelet | earring | belt | anklet`
  - especiales: `amulet`, `tattoo`
- `rarity` (enum): `common | uncommon | rare | epic | legendary | mythic`
- `tier_requirement` (enum): `C | B | A | S | SS | SSS | IV`
- `max_stack` (int >= 1)
- `durability_max` (int >= 0, opcional)
- `effects[]` (array de `effect_descriptor`)

### 2.2 `inventory_profile`

Representa estado persistente por jugador/personaje.

Campos mínimos:
- `owner_id` (string)
- `items_owned` (map): `{ item_id: qty }`
- `equipped_slots` (map): `{ slot_id: item_instance_id }`
- `tattoo_slot` (nullable string)
- `loadouts` (array de `loadout_descriptor`)

### 2.3 `combat_inventory_snapshot`

Estado de inventario congelado al iniciar combate/run.

Campos mínimos:
- `battle_id` (string)
- `allowed_items` (array de `item_instance_id`)
- `turn_usage_tracker` (objeto por turno/categoría)
- `remaining_durability` (map): `{ item_instance_id: value }`
- `run_bound_flags` (objeto): `{ from_tower: bool, temporary_item: bool, temporary_character: bool }`

### 2.4 `consumption_rules`

Reglas de validación de uso en runtime.

Campos mínimos:
- `limits_per_turn` (map): `{ category_key: max_uses }`
- `mode_restrictions` (objeto por modo: duelo/torneo/torre)
- `resolution_priority` (array): orden de aplicación de efectos

### 2.5 `reward_payload`

Contrato de salida para recompensas.

Campos mínimos:
- `gold` (int >= 0)
- `stars` (int >= 0)
- `items` (array de `item_reward_entry`)
- `tickets` (objeto): `{ C:int, B:int, A:int }`
- `characters` (array de `character_reward_entry`)

---

## 3) Tipos auxiliares

### 3.1 `effect_descriptor`
- `effect_id` (string)
- `effect_kind` (enum): `restore | buff_pct | buff_flat | convert_damage | reflect_damage | absorb_damage`
- `target_scope` (enum): `self | ally | enemy | technique`
- `value` (number)
- `duration_kind` (enum): `instant | turns | battle | run | permanent`
- `duration_value` (int, opcional)

### 3.2 `loadout_descriptor`
- `loadout_id` (string)
- `name` (string)
- `slots` (map): `{ slot_id: item_instance_id }`
- `created_at` (iso datetime)
- `updated_at` (iso datetime)

---

## 4) Ejemplo mínimo (JSON ilustrativo)

```json
{
  "item_catalog": {
    "potion_hp_red": {
      "item_id": "potion_hp_red",
      "item_type": "consumable",
      "subtype": "hp_potion",
      "rarity": "uncommon",
      "tier_requirement": "C",
      "max_stack": 20,
      "durability_max": 0,
      "effects": [
        {
          "effect_id": "hp_restore_50pct",
          "effect_kind": "restore",
          "target_scope": "self",
          "value": 0.5,
          "duration_kind": "instant"
        }
      ]
    }
  }
}
```

---

## 5) Invariantes

1. Ningún `item_id` duplicado en `item_catalog`.
2. `qty` en inventario nunca negativo.
3. Si `durability_max == 0`, ítem no usa durabilidad.
4. Un slot solo admite tipos compatibles.
5. Snapshot de combate no puede mutar el inventario global directamente.

---

## 6) Criterio de firma (Fase 0)

- Revisado por diseño + implementación + QA.
- Sin ambigüedades en tipos, rangos y validaciones.
- Compatible con UI (lobby + combate) y runtime.
