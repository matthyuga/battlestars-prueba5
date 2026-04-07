# FASE2_INVENTARIO_COMBATE_CONSUMIBLES_BASE_V1

Fecha: 2026-04-06  
Estado: Plan de ejecución (listo para implementar)

## 1) Meta

Habilitar uso real de ítems en batalla con reglas estrictas de consumo y trazabilidad completa para QA.

---

## 2) Alcance funcional (Fase 2)

### 2.1 Snapshot al iniciar combate

Al crear una batalla, generar `combat_inventory_snapshot` con:
- `battle_id`
- `owner_id`
- `allowed_items[]`
- `turn_usage_tracker`
- `remaining_durability`
- `run_bound_flags`

Reglas:
- El snapshot se congela al inicio del combate.
- No se muta inventario global directamente durante la validación de turno.
- Todo consumo válido debe reflejarse en snapshot y en log de eventos.

### 2.2 Pociones de recurso habilitadas

Tipos permitidos en Fase 2:
- HP: 25% / 35% / 50%
- EC: 25% / 35% / 50%
- EP: 25% / 35% / 50%
- Durabilidad: 25% / 35% / 50%

Mapeo sugerido por color:
- Amarilla: 25%
- Naranja: 35%
- Roja: 50%

### 2.3 Validaciones por turno

Reglas obligatorias:
1. Máximo 1 uso por tipo/color en el mismo turno.
2. Bloquear duplicado exacto dentro del turno.
3. Si falla validación, no consumir stack.
4. El consumo válido actualiza `turn_usage_tracker`.

---

## 3) Contrato operativo de turno

### 3.1 Claves de tracking sugeridas

`turn_usage_tracker[turn_number]`:
- `hp_yellow_used`
- `hp_orange_used`
- `hp_red_used`
- `ec_yellow_used`
- `ec_orange_used`
- `ec_red_used`
- `ep_yellow_used`
- `ep_orange_used`
- `ep_red_used`
- `durability_yellow_used`
- `durability_orange_used`
- `durability_red_used`

### 3.2 Reseteo de turno

Evento `on_turn_change`:
- Incrementa `turn_number`.
- Inicializa tracking del nuevo turno en `false`.
- Conserva historial de turnos previos para auditoría QA.

---

## 4) Flujo runtime (resumen)

1. Player solicita uso de consumible.
2. Validar ítem en `allowed_items`.
3. Validar stock/durabilidad.
4. Validar límite por tipo/color del turno.
5. Si válido: consumir, aplicar efecto, registrar evento.
6. Si inválido: rechazar con reason_code y loggear rechazo.

---

## 5) Logging obligatorio para QA

Registrar por evento:
- `battle_id`
- `turn_number`
- `actor_id`
- `item_id`
- `result`: `applied | rejected`
- `reason_code` (si rejected)
- `resource_before`
- `resource_after`
- `tracker_state`

`reason_code` sugeridos:
- `DUPLICATE_IN_TURN`
- `LIMIT_REACHED`
- `NO_STOCK`
- `INVALID_ITEM`
- `NOT_ALLOWED_IN_MODE`

---

## 6) Criterios de salida Fase 2

1. No se puede explotar consumo por spam.
2. El tracker por turno resetea correctamente al cambiar turno.
3. Eventos de uso quedan logueados para QA.

Criterios QA adicionales:
- Intentar doble uso mismo tipo/color en mismo turno siempre falla.
- Usar mismo tipo en turno siguiente funciona si hay stock.
- Logs incluyen `reason_code` consistente en cada rechazo.

---

## 7) Checklist de implementación

- [ ] Builder de `combat_inventory_snapshot` al iniciar combate.
- [ ] Validador de consumo por turno implementado.
- [ ] Adaptador de aplicación de efectos HP/EC/EP/Durabilidad.
- [ ] Reseteo de tracker en `on_turn_change`.
- [ ] Logger de consumo/rechazo activo.
- [ ] Smoke test manual de reglas anti-spam.

---

## 8) Entregables de Fase 2

1. `documentation/FASE2_INVENTARIO_COMBATE_CONSUMIBLES_BASE_V1.md` (este documento)
2. `documentation/CHECKLIST_QA_FASE2_CONSUMIBLES_BASE_V1.md` (pendiente)
3. `documentation/MATRIZ_CASOS_BORDE_CONSUMO_TURNO_V1.md` (pendiente)
