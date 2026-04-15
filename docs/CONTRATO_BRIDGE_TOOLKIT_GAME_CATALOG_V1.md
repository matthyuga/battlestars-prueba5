# Contrato Bridge Toolkit ⇄ Juego (Catálogos Saga) v1

Objetivo: definir un payload canónico para que la toolkit pueda inyectar catálogos de héroes/items al juego sin tocar wireframes UI.

## Payload v1

```json
{
  "heroes": [
    {"hero_id": "Harribel", "name": "Harribel", "tier": "C", "franchise": "Bleach"}
  ],
  "items": {
    "consumibles": {
      "title": "Consumibles",
      "groups": {
        "pociones": [
          {"item_id": "pocion_hp_roja", "name": "Poción HP roja", "rarity": "common", "tier_req": "C", "meta": "+50% HP", "price_gold": 120}
        ]
      }
    }
  }
}
```

## Punto de integración en juego

- API: `store.bs_set_catalog_bundle_v1(payload)`
- Lectura en Hub Saga:
  - héroes: `store.bs_get_hero_catalog_v1()`
  - ítems: `store.bs_get_item_catalog_v1()`
- Fallback: si no hay payload inyectado, el hub mantiene el esquema local wireframe.

## Regla de compatibilidad

- `heroes` puede venir vacío.
- `items` puede venir vacío.
- El juego no debe romper: usa fallback local si el payload no cumple o no existe.
