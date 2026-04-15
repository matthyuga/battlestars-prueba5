# P2-02 — Contrato Toolkit -> Lobby (Import/Export simple v0.1)

Fecha: 2026-04-14  
Estado: Congelado para integración inicial

---

## 1) Propósito

Definir un contrato JSON mínimo para intercambiar estado entre toolkit y lobby sin acoplar lógica interna.

---

## 2) Artefactos de intercambio

1. `lobby_snapshot.json` (estado importable/exportable).
2. `lobby_audit.jsonl` (eventos auditables append-only).

---

## 3) Esquema de `lobby_snapshot.json`

```json
{
  "schema_version": "lobby_contract_v0_1",
  "generated_at": "2026-04-14T00:00:00Z",
  "account_state": {
    "account_id": "local_player",
    "display_name": "Mistico",
    "level": 1,
    "exp": 0,
    "exp_to_next": 100,
    "tier": "C",
    "gold": 5000,
    "gems": 0
  },
  "heroes_owned": {
    "aqua": {
      "hero_id": "aqua",
      "owned": true,
      "level": 1,
      "exp": 0,
      "is_rotation_free": false
    }
  },
  "inventory_state": {
    "account_inventory": {
      "consumables": {"potion_hp_red": 3},
      "equipables": {},
      "materials": {}
    },
    "hero_inventories": {}
  },
  "meta": {
    "source": "lobby_runtime",
    "mode": "classic"
  }
}
```

---

## 4) Reglas de validación

1. `schema_version` obligatorio y exacto.
2. `gold >= 0`, `qty >= 0`.
3. Si hay héroe en `heroes_owned`, debe tener `owned=true`.
4. Campos desconocidos se permiten pero no pueden romper parseo.

---

## 5) Esquema de `lobby_audit.jsonl`

Cada línea es un evento JSON independiente:

```json
{"ts": 1712966400, "event": "buy_item", "payload": {"item_id": "potion_hp_red", "qty": 1, "gold_before": 5000, "gold_after": 4700}}
```

Eventos mínimos esperados v0.1:
- `buy_hero`
- `buy_item`
- `gold_delta`

---

## 6) Operaciones soportadas

## 6.1 Export

- Lobby escribe `lobby_snapshot.json` al cerrar sesión de pruebas o bajo comando manual.

## 6.2 Import

- Lobby puede cargar snapshot para reproducir escenarios (debug/QA).
- Si falla validación, rechaza import y registra error en auditoría.

---

## 7) Compatibilidad y evolución

- Versionado semántico por `schema_version`.
- Cambios breaking => `lobby_contract_v0_2`.
- Cambios additive no-breaking permitidos dentro de v0.1.

