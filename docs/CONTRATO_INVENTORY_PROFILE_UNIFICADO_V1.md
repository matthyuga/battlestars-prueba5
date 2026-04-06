# Contrato InventoryProfile Unificado (V1)

> Extensión de arquitectura para separar capacidades de inventario por clase de actor, con foco en subtipos GAMMA.

---

## 1) Objetivo

Unificar el manejo de inventario bajo un contrato común (`InventoryProfile`) que permita:

- Reutilizar pipeline de validación/carga/serialización.
- Diferenciar reglas por clase (`PLAYER/ALPHA/BETA/GAMMA/DELTA`).
- Introducir subtipos GAMMA con lógica propia:
  - `gamma_subtype`
  - `stock_profile`
  - `restock_policy`
  - `cargo_capacity`

---

## 2) Modelo conceptual

`InventoryProfile` tiene dos capas:

1. **Core común**
   - Identidad, límites base, slots, peso, monedas, flags.

2. **Extensiones por rol**
   - comercio (vendor stock)
   - logística (caravana/carga)
   - persistencia (si aplica o no en progresión)

---

## 3) Contrato canónico (`InventoryProfile`)

```json
{
  "inventory_profile_version": "1.0",
  "actor_id": "string",
  "actor_type": "PLAYER|ALPHA|BETA|GAMMA|DELTA",

  "core": {
    "enabled": true,
    "inventory_mode": "carry|vendor|hybrid|none",
    "slot_capacity": 40,
    "weight_capacity": 120.0,
    "weight_current": 35.5,
    "stack_rules": {
      "max_stack_default": 99,
      "allow_overstack": false
    },
    "currencies": {
      "oro": 1200
    },
    "allow_item_use": true,
    "allow_item_drop": true,
    "allow_item_trade": false
  },

  "gamma_extension": {
    "gamma_subtype": "none|pedestrian|merchant_shop|merchant_caravan",

    "stock_profile": {
      "stock_mode": "none|infinite|finite",
      "catalog_id": "string|null",
      "stock_items": [
        {
          "item_id": "potion_small",
          "stock_current": 12,
          "stock_max": 30,
          "buy_price": 25,
          "sell_price": 12,
          "weight_per_unit": 0.2
        }
      ]
    },

    "restock_policy": {
      "enabled": false,
      "restock_mode": "none|time_interval|daily_reset|route_node_arrival|manual",
      "interval_minutes": 60,
      "daily_reset_hour_utc": 3,
      "restock_amount_default": 5,
      "restock_to_max": false,
      "jitter_pct": 0.10,
      "next_restock_at_utc": "ISO-8601|null"
    },

    "cargo_capacity": {
      "enabled": false,
      "carrier_type": "none|beast|vehicle|cart",
      "cargo_weight_capacity": 0.0,
      "cargo_weight_current": 0.0,
      "cargo_slot_capacity": 0,
      "route_id": "string|null",
      "next_stop_at_utc": "ISO-8601|null"
    }
  },

  "persistence": {
    "save_enabled": true,
    "progression_enabled": true,
    "reward_eligible": true,
    "inventory_audit_enabled": true
  }
}
```

---

## 4) Reglas por clase (matriz)

| Clase | inventory_mode | progression_enabled | reward_eligible | stock_mode | cargo_capacity |
|---|---|---:|---:|---|---|
| PLAYER | carry/hybrid | ✅ | ✅ | none | opcional |
| ALPHA | carry/hybrid | ✅ | ✅ | opcional | opcional |
| BETA | none/carry limitado | ❌ (default) | ❌ (default) | none | no |
| GAMMA_PEDESTRIAN | none/carry mínimo | ❌ | ❌ | none | no |
| GAMMA_MERCHANT_SHOP | vendor | ❌ | ❌ | finite/infinite | no (usa almacén abstracto) |
| GAMMA_MERCHANT_CARAVAN | vendor/hybrid | ❌ | ❌ | finite | sí (obligatorio) |
| DELTA | carry/hybrid | ✅ | ✅ | opcional | opcional |

---

## 5) Subtipos GAMMA (reglas exactas)

## 5.1 `pedestrian`

- `inventory_mode = none` (o carry mínimo narrativo).
- `stock_mode = none`.
- `restock_policy.enabled = false`.
- `cargo_capacity.enabled = false`.

Uso: peatones/decoración social.

## 5.2 `merchant_shop`

- `inventory_mode = vendor`.
- `stock_mode = finite` recomendado (o `infinite` en prototipo).
- `restock_policy` activa por tiempo o reset diario.
- `cargo_capacity.enabled = false` (justificación logística: almacén/baúl local).

Uso: mercader fijo de tienda.

## 5.3 `merchant_caravan`

- `inventory_mode = vendor|hybrid`.
- `stock_mode = finite`.
- `restock_policy` por `route_node_arrival` o intervalo.
- `cargo_capacity.enabled = true`.
- Debe existir `carrier_type` y capacidad de carga > 0.

Uso: mercader móvil con justificación de peso por transporte.

---

## 6) Validaciones obligatorias

1. Si `actor_type != GAMMA`, entonces `gamma_subtype = none`.
2. Si `gamma_subtype = pedestrian`, `stock_mode` debe ser `none`.
3. Si `gamma_subtype = merchant_shop`, `stock_mode != none`.
4. Si `gamma_subtype = merchant_caravan`, `cargo_capacity.enabled = true` y `cargo_weight_capacity > 0`.
5. Si `stock_mode = finite`, todo item debe cumplir:
   - `0 <= stock_current <= stock_max`.
6. Si `restock_policy.enabled = true`, `restock_mode != none`.
7. Si `inventory_mode = none`, no se permiten operaciones de uso/drop/trade.
8. BETA/GAMMA por default: `reward_eligible = false`.

---

## 7) Eventos de inventario (mínimos)

- `INV_ADD_ITEM`
- `INV_REMOVE_ITEM`
- `INV_USE_ITEM`
- `INV_TRADE_BUY`
- `INV_TRADE_SELL`
- `INV_RESTOCK`
- `INV_CARGO_TRANSFER`
- `INV_WEIGHT_LIMIT_EXCEEDED`

Cada evento debe registrar:

- actor_id
- actor_type
- subtype (si GAMMA)
- before/after stock o carry
- source (`shop`, `battle`, `quest`, `manual`)
- timestamp

---

## 8) Integración con Shadow Ledger

- Cambios económicos (oro/ítems transaccionales) deben poder referenciar `reward_event_id` o `trade_event_id`.
- Para compra/venta de GAMMA, se recomienda `trade_event_id` propio y enlace cruzado con ledger de economía.
- Reconciliación: inventario visible vs inventario sombra por actor/tienda.

---

## 9) Ejemplos rápidos

## 9.1 PLAYER

- `inventory_mode = carry`
- peso/slots activos
- usa y consume ítems
- recibe recompensas

## 9.2 GAMMA_MERCHANT_SHOP

- `inventory_mode = vendor`
- stock finito de pociones
- restock cada 60 min
- sin capacidad de caravana

## 9.3 GAMMA_MERCHANT_CARAVAN

- `inventory_mode = vendor`
- stock finito + capacidad de carga en bestia/vehículo
- restock al llegar a nodo de ruta

---

## 10) Criterios de aceptación (QA)

- [ ] GAMMA_PEDESTRIAN no comercializa.
- [ ] GAMMA_MERCHANT_SHOP vende y repone según política.
- [ ] GAMMA_MERCHANT_CARAVAN bloquea ventas cuando no hay stock/carga.
- [ ] Peso y slots se aplican correctamente a PLAYER/ALPHA.
- [ ] BETA y GAMMA no reciben recompensas de progresión por default.
- [ ] Logs de inventario son trazables y conciliables.

---

## 11) Decisiones abiertas

1. ¿Mercaderes tienda con stock infinito solo en dificultad baja?
2. ¿Caravana puede alquilar/expandir capacidad de carga?
3. ¿Persistencia de precios dinámicos por región/escasez?
4. ¿Límite de compra por jugador para anti-farm?

