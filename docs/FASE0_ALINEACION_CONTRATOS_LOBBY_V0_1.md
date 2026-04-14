# Fase 0 — Alineación y congelación de contratos (Lobby MVP v0.1)

Fecha: 2026-04-14  
Estado: Cerrada (acta emitida)
Base:
- `docs/SPEC_LOBBY_MVP_V0_1.md`
- `docs/PLAN_TRABAJO_LOBBY_MVP_V0_1.md`
- `docs/PLAN_SPIKE_HTML_CANVAS_LOBBY_V0_1.md`

---

## 1) Objetivo de Fase 0

Cerrar alcance, contratos y criterios de salida **antes de desarrollar** para evitar retrabajo y ambigüedad funcional.

---

## 2) Scope confirmado (In/Out)

## 2.1 In-scope (entra en Lobby MVP v0.1)

1. Home lobby + navegación entre módulos.
2. Estado de cuenta visible (`gold`, `exp`, `level`, `tier`).
3. Módulo Héroes:
   - listar catálogo,
   - comprar/desbloquear,
   - mostrar roster adquirido.
4. Módulo Tienda:
   - listar ítems,
   - compra simple (`qty=1`).
5. Módulo Inventario:
   - baúl de cuenta,
   - inventario por héroe (solo lectura v0.1).
6. Auditoría mínima:
   - `buy_hero`,
   - `buy_item`,
   - movimientos de oro.

## 2.2 Out-of-scope (no entra en v0.1)

1. Integración completa con combate runtime.
2. Matchmaking/netcode/multijugador.
3. Equipamiento avanzado (durabilidad, efectos por turno).
4. Persistencia de producción cross-device.
5. Balance final de economía y recompensas.

---

## 3) Congelación de contratos de estado (v0.1)

> Regla: ningún módulo UI (classic o canvas) puede leer/escribir campos fuera de este contrato sin RFC de cambio.

## 3.1 `account_state` (congelado)

Campos obligatorios:
- `account_id: string`
- `display_name: string`
- `level: int >= 1`
- `exp: int >= 0`
- `exp_to_next: int > 0`
- `tier: string`
- `gold: int >= 0`
- `gems: int >= 0`

## 3.2 `hero_catalog_entry` (congelado)

Campos obligatorios:
- `hero_id: string`
- `name: string`
- `franchise: string`
- `tier: string`
- `price_gold: int >= 0`
- `enabled_modes: string[]`

## 3.3 `hero_owned_entry` (congelado)

Campos obligatorios:
- `hero_id: string`
- `owned: bool`
- `level: int >= 1`
- `exp: int >= 0`
- `is_rotation_free: bool`

## 3.4 `item_catalog_entry` (congelado)

Campos obligatorios:
- `item_id: string`
- `name: string`
- `item_type: string`
- `rarity: string`
- `tier_requirement: string`
- `price_gold: int >= 0`
- `stackable: bool`
- `max_stack: int >= 1`

## 3.5 `inventory_state` (congelado)

Estructura mínima:
- `account_inventory`
  - `consumables: map<string,int>`
  - `equipables: map<string,int>`
  - `materials: map<string,int>`
- `hero_inventories`
  - `<hero_id>`
    - `consumables: map<string,int>`
    - `equipables: map<string,int>`

## 3.6 `audit_event` (congelado)

Campos obligatorios:
- `ts: unix_epoch_seconds`
- `event: string`
- `payload: object`

Eventos mínimos aceptados en v0.1:
- `buy_hero`
- `buy_item`
- `gold_delta`

---

## 4) Invariantes funcionales (deben cumplirse siempre)

1. `gold` nunca puede ser negativo.
2. No se permite compra duplicada de héroe adquirido.
3. `qty` de inventario nunca negativo.
4. Si una operación falla, no muta estado parcial.
5. Toda operación económica válida genera `audit_event`.

---

## 5) Integración UI (classic/canvas) durante Fase 0

1. Se mantiene arquitectura dual bajo feature flag:
   - `lobby_classic` (estable)
   - `lobby_canvas_experimental` (opcional)
2. La UI no contiene reglas de negocio: solo renderiza + dispara casos de uso.
3. `buy_item` será la primera operación puente para validar estado compartido.

---

## 6) Criterio de salida de Fase 0

Fase 0 se considera completada cuando:

1. In/Out scope queda firmado sin ambigüedad.
2. Contratos de estado `account/heroes/inventory/audit` quedan congelados.
3. Checklist no-regresión combate queda creado y listo para ejecución.
4. Tablero P0/P1/P2 queda publicado con responsables y estado inicial.


---

## 7) Evidencia administrativa de cierre

- Acta de cierre: `docs/ACTA_CIERRE_FASE0_LOBBY_V0_1.md`.
- Tablero P0/P1/P2 actualizado con P0-07 y P0-08 en `done`.

