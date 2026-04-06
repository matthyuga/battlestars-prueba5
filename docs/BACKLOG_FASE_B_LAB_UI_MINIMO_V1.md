# Backlog Técnico — Fase B (Laboratorio UI mínimo) V1

> Objetivo Fase B: exponer en UI el motor del simulador para ejecución manual de escenarios (1v1/2v1/2v2), inspección de resultados y soporte QA.

---

## 1) Alcance de Fase B

- Pantalla de laboratorio con editor de request.
- Carga de fixtures base.
- Ejecución de `run_simulation` desde UI.
- Visualización por actor de resultados y auditoría.
- Export sencillo de salida para revisión.

No incluye (queda fuera de fase):

- Integración full al flujo real de `battle_end`.
- Eventos `mid_battle_event` productivos.
- Persistencia multiplayer host/guest.

---

## 2) Tickets (orden recomendado)

## B1 — Crear entrypoint de Laboratorio UI

**Tipo:** Feature
**Dependencias:** ninguna
**Estimación:** M

### Descripción
Crear una pantalla principal del laboratorio (`screen sim_lab_v1`) y un label de entrada para abrirla desde debug/dev.

### Entregables
- label/lanzador de laboratorio.
- estructura base del screen (layout contenedor).

### DoD
- se puede abrir/cerrar el laboratorio sin romper flujo.
- pantalla renderiza con estado inicial.

---

## B2 — Estado de UI y store local del request

**Tipo:** Feature
**Dependencias:** B1
**Estimación:** M

### Descripción
Definir `sim_lab_state` y helpers para editar request sin side effects.

### Entregables
- estado inicial = `sim_build_min_request()`.
- helper de reset a estado base.
- helper de clonado seguro (copy/deepcopy).

### DoD
- editar estado no muta referencias compartidas.
- reset devuelve request válido.

---

## B3 — Editor de modo, ganador y config

**Tipo:** Feature
**Dependencias:** B2
**Estimación:** S

### Descripción
Agregar controles para `mode`, `winner_team`, `event_type`, `source`, `preset`, `repetition_count`, `multi_factor_enabled`.

### Entregables
- botones/selección de modo.
- botones de ganador/empate.
- controles de config.

### DoD
- cambios de UI se reflejan en request.
- valores fuera de dominio no se persisten.

---

## B4 — Editor de actores/equipos

**Tipo:** Feature
**Dependencias:** B2
**Estimación:** L

### Descripción
Permitir agregar/quitar actores y editar:

- `actor_id`, `actor_type`, `team`
- `level`, `register`, `exp_current`, `oro_current`
- `flags` de elegibilidad

### Entregables
- tabla/lista editable por actor.
- alta/baja de actor.

### DoD
- al menos 1 actor siempre presente.
- cambios persisten en `sim_lab_state`.

---

## B5 — Editor de estrellas 6x0..5

**Tipo:** Feature
**Dependencias:** B4
**Estimación:** M

### Descripción
Controles por categoría (`ofensiva`, `defensiva`, `control`, `eficiencia`, `tecnica`, `impacto`) con ± y display de total.

### Entregables
- control por categoría.
- total visual por actor.

### DoD
- UI no permite salir de 0..5 por categoría.
- total visible coincide con validación backend.

---

## B6 — Integración con `run_simulation`

**Tipo:** Feature
**Dependencias:** B3, B4, B5
**Estimación:** M

### Descripción
Botón `Simular` que ejecute `run_simulation(sim_lab_state.request)` y guarde output.

### Entregables
- acción de simulación.
- estructura de resultado en estado UI.

### DoD
- simulación devuelve `results[]` y `audit`.
- en caso inválido se muestran errores de validación.

---

## B7 — Panel de resultados por actor

**Tipo:** Feature
**Dependencias:** B6
**Estimación:** M

### Descripción
Mostrar por actor:

- `outcome`, `eligible`
- `stars_total`, `delta_register`
- `base exp/oro`
- `exp_gain/oro_gain`
- `exp_after/oro_after`
- multiplicadores aplicados

### DoD
- cada actor del request tiene bloque de resultado.
- los datos coinciden con output del motor.

---

## B8 — Panel de auditoría e idempotencia

**Tipo:** Feature
**Dependencias:** B6
**Estimación:** M

### Descripción
Mostrar:

- `audit.errors`
- `audit.warnings`
- bloque `audit.idempotency` (enabled/event/statuses)

### DoD
- duplicados de `reward_event_id` se visualizan claramente.
- usuario ve si el pago fue ignorado/conflictivo.

---

## B9 — Carga de fixtures A/B/C

**Tipo:** Feature
**Dependencias:** B2
**Estimación:** S

### Descripción
Botones para cargar fixtures de `sim_phaseA_fixture_requests()`:

- fixture_a_2v2
- fixture_b_2v1
- fixture_c_1v1_dr0

### DoD
- cada botón reemplaza request actual por fixture seleccionado.
- fixture cargado simula sin errores de contrato.

---

## B10 — Export de resultado para QA

**Tipo:** Feature
**Dependencias:** B6
**Estimación:** S

### Descripción
Botón de export (texto JSON) usando `sim_export_phaseA_fixtures_json()` o serialización de última corrida.

### DoD
- salida exportable/copiable desde UI.
- formato consistente para diff manual.

---

## B11 — Smoke checklist de Fase B

**Tipo:** QA
**Dependencias:** B1..B10
**Estimación:** S

### Casos mínimos
1. Simulación 1v1 (victoria/derrota/draw).
2. Simulación 2v1 con `m_multi` activo.
3. Actor GAMMA forzado a no elegible.
4. Duplicado `reward_event_id` muestra `DUPLICATE_IGNORED`.
5. Carga de fixture + simulación + export JSON.

### DoD
- checklist completo en sesión QA.
- sin crashes UI/acción en flujo principal.

---

## 3) Orden de ejecución (plan corto)

1. B1 → B2
2. B3 + B4 + B5
3. B6
4. B7 + B8
5. B9 + B10
6. B11 (cierre)

---

## 4) Riesgos y mitigación

### Riesgo 1: UI sobrecargada
- **Mitigación:** panel por secciones colapsables (Request / Result / Audit).

### Riesgo 2: estado inconsistente al editar actores
- **Mitigación:** normalizar por `sim_validate_request` antes de simular.

### Riesgo 3: confusión con idempotencia
- **Mitigación:** mostrar `statuses` por actor con etiquetas claras.

### Riesgo 4: diferencia entre helper tests y runtime real
- **Mitigación:** ejecutar B11 manual + snapshots de salida JSON.

---

## 5) Criterio de salida de Fase B

Se considera completa cuando:

- [ ] laboratorio abre y permite simular 1v1/2v1/2v2.
- [ ] request es editable (actores, estrellas, config).
- [ ] resultados y auditoría se visualizan por actor.
- [ ] fixtures A/B/C se cargan y ejecutan.
- [ ] export JSON está disponible para QA.
- [ ] smoke B11 sin bloqueantes.

