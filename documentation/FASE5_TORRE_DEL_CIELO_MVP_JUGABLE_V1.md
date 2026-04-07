# FASE5_TORRE_DEL_CIELO_MVP_JUGABLE_V1

Fecha: 2026-04-06  
Estado: Plan de ejecución (listo para implementar)

## 1) Meta

Lograr una corrida completa y estable de Torre del Cielo en tiers bajos, con recompensas mixtas y cierre correcto de run.

---

## 2) Alcance funcional (Fase 5)

### 2.1 Bloques de Torre habilitados

Alcance MVP:
- Bloques **C/B** obligatorios.
- Bloques **A** opcionales según estabilidad QA.

Rangos sugeridos:
- C: pisos 1-20
- B: pisos 21-50
- A (opcional): pisos 51-90

### 2.2 Buffs temporales de run

Tipos de buff temporal permitidos en MVP:
- aumento de daño (%)
- reducción de daño recibido (%)
- regeneración parcial de HP/EC/EP por combate
- mejora de bloqueo/defensa (%), sujeto a cap

Reglas:
- Se aplican solo dentro de la run activa.
- Deben expirar al finalizar/abandonar Torre.
- Deben registrarse en `run_state.active_buffs`.

### 2.3 Personajes temporales de run

Soporte MVP:
- Drops/eventos pueden otorgar personajes temporales.
- El personaje temporal solo existe durante la run salvo conversión explícita.

Reglas iniciales de permanencia:
- `is_temporary = true` por defecto.
- Solo pasa a permanente si se cumple condición de conversión (quest/hito/evento).
- Al cerrar run sin conversión, remover de roster persistente.

### 2.4 Tickets de torneo como loot raro

Tipos de ticket soportados:
- `ticket_torneo_c`
- `ticket_torneo_b`
- `ticket_torneo_a`

Reglas:
- Drop de baja probabilidad.
- Debe quedar registrado en `reward_payload.items/tickets`.
- Persistencia inmediata al confirmar fin de run.

---

## 3) Estado de run (contrato operativo)

`tower_run_state` mínimo:
- `run_id`
- `owner_id`
- `current_floor`
- `current_block`
- `active_buffs[]`
- `temporary_characters[]`
- `run_rewards_buffer`
- `run_status` (`active|completed|abandoned|failed`)

Transiciones:
1. `active` → `completed` (llegó a meta del MVP)
2. `active` → `failed` (derrota)
3. `active` → `abandoned` (salida manual)

---

## 4) Flujo MVP de Torre

1. Iniciar run (crear `tower_run_state`).
2. Entrar a piso/bloque.
3. Resolver combate.
4. Aplicar recompensa del piso (oro/items/buff/ticket/personaje temporal).
5. Actualizar estado de run.
6. Repetir hasta completar objetivo o fallar.
7. Cerrar run y consolidar recompensas persistentes.

---

## 5) Cierre de run y persistencia

Al cerrar run:
- Consolidar oro/estrellas/items/tickets válidos.
- Eliminar buffs temporales de run.
- Resolver permanencia de personajes temporales.
- Emitir `tower_run_summary` auditable.

Campos mínimos de resumen:
- `run_id`
- `floors_cleared`
- `max_floor_reached`
- `rewards_granted`
- `temporary_characters_converted`
- `temporary_characters_removed`
- `run_end_reason`

---

## 6) Criterios de salida Fase 5

1. Run completa sin bloqueos.
2. Recompensas aplicadas correctamente al salir de Torre.

Criterios QA adicionales:
- `abandoned` y `failed` también cierran sin corrupción de estado.
- No persisten buffs temporales fuera de Torre.
- Tickets raros se guardan correctamente cuando dropean.

---

## 7) Checklist de implementación

- [ ] Implementar `tower_run_state` y transiciones de estado.
- [ ] Activar bloques C/B (A opcional bajo flag).
- [ ] Integrar buffs temporales de run.
- [ ] Integrar personajes temporales + regla de conversión inicial.
- [ ] Integrar tickets C/B/A como loot raro.
- [ ] Implementar consolidación y limpieza al cerrar run.
- [ ] Ejecutar smoke QA de run completa + run fallida + abandono.

---

## 8) Entregables de Fase 5

1. `documentation/FASE5_TORRE_DEL_CIELO_MVP_JUGABLE_V1.md` (este documento)
2. `documentation/CHECKLIST_QA_FASE5_TORRE_MVP_V1.md` (pendiente)
3. `documentation/CONTRATO_TOWER_RUN_STATE_V1.md` (pendiente)
