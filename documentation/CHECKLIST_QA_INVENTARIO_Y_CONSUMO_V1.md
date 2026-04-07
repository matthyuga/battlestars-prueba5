# CHECKLIST_QA_INVENTARIO_Y_CONSUMO_V1

Fecha: 2026-04-07  
Estado: Checklist operativo (Sprint 1)

## 1) Objetivo

Validar end-to-end el flujo de inventario (lobby) + consumo en combate (Fase 1 + Fase 2) sin inconsistencias de estado.

---

## 2) Precondiciones

- Build con contrato `inventory_contract_version=v1`.
- Personaje de prueba con ítems en inventario.
- Presets base habilitados (`balanceado|ofensivo|defensivo`).
- Log de eventos de combate activo.

---

## 3) Casos de Inventario Lobby (Fase 1)

### 3.1 Alta/Baja de ítems
- [ ] Alta de ítem incrementa `qty` correctamente.
- [ ] Baja de ítem decrementa `qty` correctamente.
- [ ] `qty` nunca queda en negativo.

### 3.2 Equipamiento por slots MVP
- [ ] Equipar anillo en slot válido funciona.
- [ ] Intentar equipar subtype inválido en slot falla con error controlado.
- [ ] Validación tier/rareza bloquea equipamiento inválido.
- [ ] Tatuaje permite solo 1 activo por personaje.

### 3.3 Presets
- [ ] Guardar preset balanceado funciona.
- [ ] Cargar preset ofensivo aplica slots correctamente.
- [ ] Sobrescribir preset defensivo funciona.
- [ ] Cargar preset con ítem faltante devuelve error controlado.

---

## 4) Casos de Consumo en Combate (Fase 2)

### 4.1 Snapshot
- [ ] `combat_inventory_snapshot` se crea al iniciar combate.
- [ ] `allowed_items` refleja inventario permitido.
- [ ] `turn_usage_tracker` inicia vacío/false.

### 4.2 Consumo válido
- [ ] HP amarilla aplica 25% y descuenta stock.
- [ ] EC naranja aplica 35% y descuenta stock.
- [ ] EP roja aplica 50% y descuenta stock.
- [ ] Durabilidad amarilla aplica 25% en ítem compatible.

### 4.3 Reglas anti-spam
- [ ] Doble uso mismo tipo/color en mismo turno es rechazado.
- [ ] Uso en turno siguiente funciona si hay stock.
- [ ] Rechazo no consume stock.

### 4.4 Reseteo de turno
- [ ] `on_turn_change` incrementa turno.
- [ ] Tracker del nuevo turno se reinicia.
- [ ] Historial de turnos previos se conserva.

---

## 5) Logs y auditoría

- [ ] Cada evento registra `battle_id`, `turn_number`, `actor_id`, `item_id`.
- [ ] Eventos rechazados incluyen `reason_code`.
- [ ] Se registran `resource_before` y `resource_after`.
- [ ] `tracker_state` es consistente con el resultado.

`reason_code` esperados:
- `DUPLICATE_IN_TURN`
- `LIMIT_REACHED`
- `NO_STOCK`
- `INVALID_ITEM`
- `NOT_ALLOWED_IN_MODE`

---

## 6) Resultado de ejecución

- [ ] PASS global (sin bloqueos críticos)
- [ ] FAIL con bugs críticos documentados
- [ ] N/A por dependencia no disponible

Observaciones QA:
- ...

Bugs levantados:
- ...
