# BACKLOG FASE D — Recompensas Mid-Battle Condicionadas (D1..D7)

Estado: **Propuesto (listo para ejecución)**  
Owner: Gameplay/Systems/QA  
Dependencias previas: Fase C (C1..C6) cerrada.

---

## Objetivo de Fase D
Habilitar recompensas parciales durante combate (`mid_battle_event`) con reglas claras, idempotencia por trigger y reconciliación segura con `battle_end`.

## Done global de Fase D
- [ ] Al menos **2 eventos mid-battle** funcionando end-to-end.
- [ ] Trigger duplicado **no paga dos veces**.
- [ ] `battle_end` **respeta pagos previos** de mid-battle (sin doble pago).

---

## D1 — Catálogo canónico de eventos mid-battle
**Tipo:** Feature / Contract  
**Prioridad:** Alta  
**Estimación:** M

### Objetivo
Definir catálogo cerrado de eventos válidos para `source=mid_battle_event`.

### Alcance mínimo v1
- `passive_proc`
- `technique_proc`
- (opcional v1.1) `item_proc`

### Entregables
- Estructura de catálogo en código (`SIM_MID_BATTLE_EVENT_CATALOG_V1` o equivalente).
- Schema de payload por tipo de evento.
- Reglas de elegibilidad por actor (PLAYER/ALPHA/DELTA).

### DoD
- Catálogo validable por función (`sim_validate_mid_battle_event`).
- Evento no catalogado => error explícito + no pago.

---

## D2 — Bridge evento -> Partial SimulationRequest
**Tipo:** Feature  
**Prioridad:** Alta  
**Dependencias:** D1  
**Estimación:** M

### Objetivo
Construir request parcial para eventos mid-battle.

### Entregables
- `sim_build_request_from_mid_battle_event(event_ctx, battle_ctx=None)`.
- Request con:
  - `source="mid_battle_event"`
  - `event_type="conditional_gain"`
  - `reward_event_id` determinístico por trigger
  - actores afectados + contexto de equipos.

### DoD
- Output pasa `sim_validate_request`.
- Compatible con `run_simulation` sin branch especial.

---

## D3 — Aplicación inmediata + idempotencia por trigger
**Tipo:** Feature  
**Prioridad:** Alta  
**Dependencias:** D2  
**Estimación:** M

### Objetivo
Ejecutar pipeline de recompensa parcial en tiempo real de combate.

### Entregables
- `sim_run_mid_battle_event(event_ctx, battle_ctx=None)` que haga:
  1. build request parcial,
  2. run_simulation,
  3. persist audit/idempotency,
  4. apply rewards.
- Reuso de `reward_event_id` + `idempotency_registry` por trigger.

### DoD
- Mismo trigger repetido => `DUPLICATE_IGNORED` y gains 0.
- Se guarda snapshot auditable de cada intento.

---

## D4 — Reconciliación con battle_end
**Tipo:** Feature / Reconciliation  
**Prioridad:** Alta  
**Dependencias:** D3  
**Estimación:** M-L

### Objetivo
Evitar doble pago entre ganancias mid-battle y cierre de combate.

### Estrategia recomendada
- Ledger parcial por combate (`sim_mid_battle_grants_v1[match_id]`) con acumulados.
- En `battle_end`, aplicar una de estas políticas:
  - **policy_subtract_paid**: cierre descuenta lo ya pagado.
  - **policy_component_lock**: componentes ya pagados no se reaplican.

### Entregables
- Hook de reconciliación en flujo de cierre.
- Reporte explícito de ajuste (`reconciliation_delta`) en audit.

### DoD
- Con eventos mid-battle previos, `battle_end` no duplica montos.
- Audit muestra cálculo bruto, ya pagado y neto final.

---

## D5 — Guard rails de economía (anti-spam)
**Tipo:** Safety  
**Prioridad:** Media-Alta  
**Dependencias:** D3  
**Estimación:** S-M

### Objetivo
Limitar explotación de triggers repetibles.

### Entregables
Parámetros de control por match:
- `max_mid_battle_grants_per_match`
- `max_mid_battle_reward_ratio` (ej. 0.40 del total proyectado)
- cooldown mínimo por `event_key` (opcional)

### DoD
- Exceder límite => no pago + warning auditado.
- No afecta reward de cierre salvo por reconciliación de D4.

---

## D6 — QA E2E extendido para mid-battle
**Tipo:** QA  
**Prioridad:** Alta  
**Dependencias:** D4, D5  
**Estimación:** M

### Objetivo
Agregar batería QA específica de Fase D.

### Casos mínimos
1. `passive_proc` paga una vez.
2. `technique_proc` paga una vez.
3. Retry mismo trigger no paga.
4. Mid-battle + battle_end no duplica.
5. Caso multi (2v1 o 2v2) con actor ALPHA/DELTA.

### Entregables
- `sim_run_phaseD_e2e_tests()`.
- Integración en `sim_lab_run_smoke_checklist()`.

### DoD
- Suite completa verde en helpers.
- Si falla, detalle legible por test.

---

## D7 — UI mínima de inspección (QA view)
**Tipo:** UX/QA  
**Prioridad:** Media  
**Dependencias:** D3  
**Estimación:** S-M

### Objetivo
Dar visibilidad de los grants mid-battle sin instrumentación externa.

### Entregables
- Panel/lista de últimos eventos mid-battle aplicados (N recientes).
- Campos mínimos:
  - `event_key`, `reward_event_id`, actor, gains, status idempotencia.
- Botón de limpieza de vista (no borra ledger persistente).

### DoD
- QA puede confirmar qué se pagó y qué se ignoró por duplicado.

---

## Orden recomendado de ejecución
1. **D1** Catálogo
2. **D2** Bridge parcial
3. **D3** Pipeline mid-battle
4. **D4** Reconciliación battle_end
5. **D5** Guard rails
6. **D6** QA E2E
7. **D7** UI inspección

---

## Riesgos y mitigaciones
- Riesgo: doble pago por triggers semánticamente iguales con IDs distintos.  
  Mitigación: `reward_event_id` determinístico + `event_key` canónico.

- Riesgo: inflación por spam de eventos en combates largos.  
  Mitigación: límites D5 + ratio máximo por match.

- Riesgo: drift entre apply real y resumen visual.  
  Mitigación: UI consume artifacts de runtime/audit, no recalcula.

---

## Criterio de salida de Fase D
Fase D se considera cerrada cuando:
- D1..D6 completados y verificados.
- D7 opcional completado o explícitamente diferido.
- No hay duplicación entre `mid_battle_event` y `battle_end` en smoke E2E.
