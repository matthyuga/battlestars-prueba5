# CONTRATO_RECOMPENSAS_ORO_ESTRELLAS_ITEMS_V1

Fecha: 2026-04-06  
Estado: Draft SSOT (Fase 0)

## 1) Objetivo

Unificar el payload de recompensas de Duelo/Torneo/Torre para evitar reglas duplicadas entre UI y runtime.

---

## 2) Estructura `reward_payload`

Campos:
- `battle_id` (string)
- `mode` (enum): `duelo | torneo | torre`
- `tier_context` (enum): `C | B | A | S | SS | SSS | IV`
- `gold` (int >= 0)
- `stars` (int >= 0)
- `items` (array)
- `tickets` (objeto)
- `characters` (array)
- `temporary_buffs` (array, opcional)
- `notes` (string opcional)

Ejemplo:
```json
{
  "battle_id": "BTL-001",
  "mode": "duelo",
  "tier_context": "B",
  "gold": 250,
  "stars": 3,
  "items": [{"item_id": "potion_hp_yellow", "qty": 1}],
  "tickets": {"C": 0, "B": 1, "A": 0},
  "characters": [],
  "temporary_buffs": []
}
```

---

## 3) Reglas por modo

### 3.1 Duelo
- Otorga principalmente oro.
- Estrellas opcionales por hitos/eventos.
- Personajes: normalmente no.

### 3.2 Torneo
- Recompensa principal: personaje por tier objetivo.
- Duplicados convierten a estrellas.
- Puede incluir tickets e ítems raros.

### 3.3 Torre
- Recompensas mixtas: oro, ítems, buffs temporales, tickets y personajes.
- Debe marcar explícitamente qué recompensa es temporal de run.

---

## 4) Integridad y auditoría

1. Todo `reward_payload` requiere `battle_id`.
2. Valores numéricos no negativos.
3. `characters` deben incluir bandera `is_temporary` cuando aplique.
4. Si hay conversión de duplicado a estrellas, registrar `source_character_id`.
5. Persistir log auditable para replay QA.

---

## 5) Campos sugeridos de telemetría

- `gold_earned_total`
- `stars_earned_total`
- `reward_variance_bucket`
- `efficiency_score`
- `damage_effective`
- `block_effective`
- `resource_spend_ec_ep`

---

## 6) Criterio de firma (Fase 0)

- Payload estable y versionado (`reward_contract_version=v1`).
- Consumible por UI de resultados y por persistencia runtime.
- Cobertura QA de casos de recompensa mixta y duplicados.
