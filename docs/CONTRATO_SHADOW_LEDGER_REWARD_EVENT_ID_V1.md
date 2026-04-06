# Contrato Shadow Ledger + Reward Event ID (V1)

> Documento focalizado en trazabilidad, anti-duplicación y consistencia de recompensas (EXP/Oro/ítems).

---

## 1) Objetivo

Definir una capa de auditoría robusta para recompensas mediante:

- `reward_event_id` único por evento de recompensa.
- `ShadowLedgerEntry` append-only para trazabilidad completa.
- Detección de duplicados, replay y cambios no respaldados.

Este documento se centra en la pieza de seguridad/consistencia y no en el balance matemático del simulador.

---

## 2) Problema que resuelve

Sin ledger sombra, el estado visible (oro/exp/items) puede desviarse del historial real por:

1. doble aplicación del mismo evento,
2. reintentos de red/UI sin idempotencia,
3. alteraciones no autorizadas de estado,
4. discrepancias entre `mid_battle_event` y `battle_end`.

La política de blueprint ya exige no duplicar y mantener trazabilidad completa. (ver criterios QA y reglas de eventos)

---

## 3) `reward_event_id` (idempotencia)

## 3.1 Definición

`reward_event_id` = identificador único de intención de recompensa.

Debe ser estable por evento lógico, no por intento técnico.

Ejemplos de formato:

- `be::<match_id>::<actor_id>::<slot>` para cierre de combate.
- `mb::<match_id>::<actor_id>::<trigger_id>::<turn>` para mid-battle.
- `lb::<simulation_id>::<actor_id>::<run_id>` para laboratorio.

## 3.2 Regla de unicidad

Único en combinación:

`(reward_event_id, actor_id, source_scope)`

Si el mismo evento llega dos veces, la segunda aplicación se rechaza como duplicado.

## 3.3 Resultado esperado

- primera llegada: `APPLY_OK`
- repetición exacta: `DUPLICATE_IGNORED`
- payload distinto con mismo id: `DUPLICATE_CONFLICT`

---

## 4) `ShadowLedgerEntry` v1.0 (canónico)

```json
{
  "ledger_version": "1.0",
  "entry_id": "uuid-v7",
  "reward_event_id": "string-unique",
  "created_at_utc": "ISO-8601",
  "session_id": "string",
  "match_id": "string|null",
  "simulation_id": "string|null",

  "stage": "single_player|local_multiplayer|server_multiplayer",
  "source": "battle_end|mid_battle_event|lab_manual|quest_reward|shop_refund|admin_adjustment",
  "event_type": "reward_apply|reward_revert|correction|snapshot_anchor",

  "actor": {
    "actor_id": "string",
    "actor_type": "PLAYER|ALPHA|BETA|GAMMA|DELTA",
    "owner_scope": "host|guest|local",
    "team": "A|B|NONE"
  },

  "context": {
    "mode": "1v1|2v1|1v2|2v2|custom|non_combat",
    "winner_team": "A|B|DRAW|NONE",
    "delta_register": -5,
    "stars_total": 22,
    "repetition_count": 1,
    "reward_config_version": "string"
  },

  "economy_delta": {
    "exp_gain": 198,
    "oro_gain": 97,
    "items_gain": [{ "item_id": "amulet_x", "qty": 1 }],
    "items_spend": [{ "item_id": "potion_small", "qty": 1 }]
  },

  "balance_math": {
    "base_exp": 112,
    "base_oro": 59,
    "multipliers": {
      "risk_exp": 1.55,
      "risk_oro": 1.28,
      "result_exp": 1.0,
      "result_oro": 1.0,
      "performance_exp": 1.14,
      "performance_oro": 1.02,
      "antiabuso": 1.0,
      "multi_factor": 1.0
    }
  },

  "state_before": {
    "level": 12,
    "register": 1,
    "exp_current": 342,
    "oro_current": 1143
  },

  "state_after": {
    "level": 13,
    "register": 1,
    "exp_current": 540,
    "oro_current": 1240
  },

  "integrity": {
    "seq_actor": 148,
    "prev_entry_hash": "hex-string",
    "entry_hash": "hex-string",
    "sig_scheme": "none|hmac_sha256|ed25519",
    "signature": "base64|null",
    "nonce": "string|null"
  },

  "flags": {
    "duplicate_detected": false,
    "applied": true,
    "reconciled": true,
    "suspicious": false
  },

  "notes": ["level_up:+1"],
  "meta": {
    "client_build": "string",
    "platform": "string",
    "ip_hint": "string|null"
  }
}
```

---

## 5) Constraints obligatorios

1. `entry_id` único global.
2. `seq_actor` monotónico estricto por actor.
3. `prev_entry_hash` enlaza con el último entry válido del actor.
4. `entry_hash = H(canonical_json_without_signature)`.
5. Si `flags.applied=true`, `state_after` debe cuadrar con `state_before + economy_delta`.
6. `stars_total` clamp 0..30.
7. `GAMMA` no recibe recompensa de combate por defecto.
8. No se aplica dos veces el mismo `reward_event_id`.

---

## 6) Reglas por etapa de producto

## 6.1 Single player (actual)

- Firma sugerida: `hmac_sha256` local.
- Hash chain por actor.
- Reconciliación cada N eventos.
- Detección de mismatch: visible vs replay ledger.

> Nota: detecta manipulación casual/moderada, no blindaje absoluto.

## 6.2 Multiplayer local (mediano plazo)

- Host como autoridad de sesión.
- Guest propone; host valida y aplica entry final.
- Anti-replay por `reward_event_id + nonce + seq_actor`.

## 6.3 Multiplayer servidor (largo plazo)

- Servidor autoritativo.
- Firma asimétrica (`ed25519`) en entries finales.
- Cliente no confirma recompensa por sí solo.

---

## 7) Flujo `reward_apply`

1. Construir entry candidato.
2. Validar contrato y constraints.
3. Verificar duplicado por `reward_event_id`.
4. Verificar `seq_actor` + `prev_entry_hash`.
5. Calcular hash/firma.
6. Persistir entry.
7. Aplicar mutación visible.
8. Marcar `applied=true`.
9. Ejecutar reconciliación rápida.

---

## 8) Flujos de corrección

## 8.1 `reward_revert`

Se usa cuando un apply válido debe deshacerse por rollback/regla de diseño.

## 8.2 `correction`

Se usa para compensación cuando hay inconsistencia detectada.

Regla: **nunca borrar historial**, siempre append-only.

---

## 9) Códigos de error sugeridos

- `LEDGER_DUPLICATE_EVENT`
- `LEDGER_DUPLICATE_CONFLICT`
- `LEDGER_SEQ_OUT_OF_ORDER`
- `LEDGER_PREV_HASH_MISMATCH`
- `LEDGER_SIGNATURE_INVALID`
- `LEDGER_ACTOR_NOT_ELIGIBLE`
- `LEDGER_STATE_RECONCILE_FAIL`
- `LEDGER_REPLAY_DETECTED`

---

## 10) Reconciliación

## 10.1 Reconciliación rápida (por evento)

Tras cada `reward_apply`, recalcular estado esperado del actor y comparar.

## 10.2 Reconciliación por lote

Cada `N` eventos o al cargar partida:

- replay del ledger por actor,
- comparación con estado visible,
- registro de anomalías.

## 10.3 Política ante anomalía

1. marcar `suspicious=true`,
2. congelar nuevos `reward_apply` para ese actor (opcional),
3. generar `correction` si procede,
4. auditar incidente.

---

## 11) Retención y auditoría

Guardar por actor:

- último hash válido,
- contador `seq_actor`,
- últimas `N` entradas en caliente,
- snapshots `snapshot_anchor` periódicos,
- métricas de anomalías (conteo, frecuencia, severidad).

---

## 12) Criterios de aceptación (mínimos)

- [ ] Duplicado exacto de `reward_event_id` no incrementa EXP/Oro/ítems.
- [ ] Conflicto de payload para mismo id se detecta y bloquea.
- [ ] `seq_actor` desordenado se rechaza.
- [ ] Hash chain rota se detecta.
- [ ] Reconciliación detecta discrepancia visible/sombra.
- [ ] Existe trazabilidad total por actor de todas las mutaciones económicas.

---

## 13) Integración con blueprint existente

Este documento complementa y aterriza en detalle:

- la regla de no duplicación por `reward_event_id`,
- la bitácora/auditoría,
- y los criterios QA de trazabilidad.

Se mantiene compatible con el flujo definido en el blueprint del simulador.

