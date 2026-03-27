# Contrato de integración — Ítems + Furia Infernal (v1)

**Fecha:** 2026-03-27  
**Estado:** Aprobado para implementación incremental  
**Scope:** Integrar la variante *Furia Infernal* (multiplica daño total del turno) con el futuro sistema de ítems, reutilizando el placeholder ya alojado en combate.

---

## 1) Objetivo funcional

Permitir que jugador (y opcionalmente NPC) active **Dados de Furia Infernal** cuando posea/consuma el ítem correspondiente.

Reglas v1:
- Furia Infernal multiplica el **daño total ofensivo del turno** (no técnica individual).
- Tirada base: 5 dados (`5d`) con la misma tabla que Furia normal:
  - `5/5 éxitos` => `x3`
  - `3-4/5 éxitos` => `x2`
  - `0-2/5 éxitos` => `x1`
- Gate requerido:
  - `fury_infernal_feature_enabled == True`
  - poseer ítem infernal del lado correspondiente

---

## 2) APIs existentes (placeholder actual)

Ya disponibles en runtime (`renpy.store`):
- `roll_5d_infernal_fury()`
- `can_use_infernal_fury_dice(side="player"|"enemy")`
- `bs_try_apply_infernal_fury(total_damage, side="player"|"enemy")`

Flags store actuales:
- `player_has_infernal_fury_item: bool`
- `enemy_has_infernal_fury_item: bool`
- `fury_infernal_feature_enabled: bool` (default `False`)

---

## 3) Contrato de Inventario/Ítems (cuando exista)

### 3.1 IDs canónicos

- `item_id`: `fury_infernal_dice`
- `item_type`: `consumable_battle` (recomendado v1)

### 3.2 Payload mínimo de ítem

```json
{
  "id": "fury_infernal_dice",
  "name": "Dados de Furia Infernal",
  "stackable": true,
  "max_stack": 99,
  "battle_usable": true,
  "consumption": "per_battle_activation"
}
```

### 3.3 Funciones que debe exponer Inventario (contrato mínimo)

- `inv_has_item(item_id, owner="player") -> bool`
- `inv_consume_item(item_id, qty=1, owner="player") -> dict`
  - respuesta recomendada:

```json
{
  "ok": true,
  "item_id": "fury_infernal_dice",
  "consumed": 1,
  "remaining": 3
}
```

---

## 4) Flujo de integración recomendado

### Fase A — Bridge pasivo (sin consumo)

Objetivo: Inventario solo informa posesión.

1. Al iniciar combate:
   - `S.player_has_infernal_fury_item = inv_has_item("fury_infernal_dice", "player")`
2. Mantener `S.fury_infernal_feature_enabled = False` en producción hasta habilitación controlada.

### Fase B — Activación con consumo

1. Definir momento de consumo (recomendado):
   - **cuando realmente se aplica** infernal (`used=True`), no al iniciar turno.
2. Si `bs_try_apply_infernal_fury(...).used == True`:
   - ejecutar `inv_consume_item("fury_infernal_dice", 1, "player")`
3. Si consumo falla:
   - degradar a no-op y loggear warning.

### Fase C — UX/UI

1. Mostrar indicador en selector/HUD:
   - `Infernal disponible` si `can_use_infernal_fury_dice("player") == True`.
2. Tooltip sugerido:
   - “Multiplica el daño total del turno ofensivo. Requiere ítem.”

---

## 5) Orden de multiplicadores (fuente de verdad)

Para mantener consistencia de daño:

1. **Valor base técnica**
2. Multiplicadores de técnica (pociones/equip/bonos)
3. **Concentrar / Focus**
4. **Furia normal** (si aplica, técnica puntual)
5. **Suma de daño del turno**
6. **Furia Infernal** (si aplica, total del turno)

> Regla de no ambigüedad: Furia Infernal siempre opera **después** de cerrar daño del turno.

---

## 6) Telemetría y logs (obligatorio)

Registrar como mínimo:
- `infernal_fury_attempted: bool`
- `infernal_fury_used: bool`
- `infernal_fury_successes: int`
- `infernal_fury_multiplier: int`
- `infernal_fury_damage_in: int`
- `infernal_fury_damage_out: int`
- `infernal_item_consumed: int`

Formato recomendado de log humano:
- `👹 Furia Infernal (4/5): x2 al daño total.`

---

## 7) Compatibilidad 1v1 / 2v2

- En **1v1**: aplica sobre el total ofensivo del actor del turno.
- En **2v2**: aplica sobre el total ofensivo del actor activo (antes de resolver colas por target).
- No debe romper:
  - `offensive_damage_plan`
  - colas `pending_damage_by_key`
  - semántica de daño directo/defendible existente.

---

## 8) Criterios de aceptación

- [ ] Con `feature OFF`, comportamiento idéntico al actual.
- [ ] Con `feature ON` + ítem presente, infernal puede activar multiplicador total.
- [ ] Sin ítem, infernal no activa aunque `feature ON`.
- [ ] Si consumo de ítem falla, combate no crashea (fallback no-op).
- [ ] Logs de infernal visibles en combate.

---

## 9) Riesgos y mitigaciones

- **Riesgo:** doble multiplicación accidental (furia técnica + infernal aplicada dos veces).  
  **Mitigación:** mantener infernal en un único hook de cierre de ofensiva.

- **Riesgo:** desync entre inventario y flags store.  
  **Mitigación:** sincronizar flags en inicio de combate + tras consumo.

- **Riesgo:** regresión en 2v2 por daño en cola.  
  **Mitigación:** QA dedicado con casos `single_target` y `split_equal`.

---

## 10) Implementación mínima sugerida (checklist técnico)

1. Bridge inventario → flags infernal al inicio de combate.
2. Activar `fury_infernal_feature_enabled` por entorno/dev toggle.
3. Añadir consumo de ítem cuando `used=True` en infernal.
4. QA smoke 1v1 + 2v2.
5. Habilitación gradual.

---

## 11) Nota de versionado

Este contrato define la **v1 funcional** para integración con inventario.
Extensiones futuras (v2+) posibles:
- tablas de probabilidad distintas por rareza de ítem,
- variantes de costo (consumo por combate vs por activación),
- restricciones por modo (historia/entrenamiento/ranked).
