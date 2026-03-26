# Fase 7 — QA de aceptación (gate de merge final)

## Objetivo

Cerrar la propuesta del registro de combate con una validación funcional/visual reproducible, usando como **criterios de aceptación** los definidos en Fase 0.

Fuente de criterios base: `docs/PHASE0_COMBAT_LOG_DIAGNOSTICO_EJECUTIVO.md`.

---

## Gate de aceptación (debe cumplir TODO)

- [ ] Técnicas canónicas visibles en player/enemy (incluye Directo y Negador).
- [ ] `force_strong` muestra línea defensiva explícita (no solo operación).
- [ ] Costos unificados: aparece `Energía` (no `Ene` ni `E`).
- [ ] `Daño total` explicita desglose cuando hay mezcla (`defendibles` + `directos`).
- [ ] Debug técnico oculto por defecto en log narrativo.
- [ ] Operación ofensiva / Target / Cola 2v2 se pueden expandir/colapsar.

> Regla de cierre: si cualquiera queda en “No”, **no mergear**.

---

## Escenarios obligatorios (planilla)

## Escenario A — 1v1 normal

**Objetivo:** validar plantilla base ofensiva/defensiva y costos unificados.

| Check | Resultado (Sí/No) | Evidencia |
|---|---|---|
| Técnica ofensiva usa formato canónico (`Inflige ... de daño.`) |  |  |
| Técnica defensiva aparece con línea explícita |  |  |
| Costos muestran `Reiatsu / Energía` |  |  |
| No aparece `Ene` ni `E` |  |  |
| Debug oculto por defecto |  |  |

---

## Escenario B — 1v1 con Directo / Negador

**Objetivo:** validar técnicas con dados y contrato de daño mixto.

| Check | Resultado (Sí/No) | Evidencia |
|---|---|---|
| `Ataque Directo` sigue patrón canónico de texto |  |  |
| `Ataque Negador` sigue patrón canónico y color ofensivo |  |  |
| Texto de condición (2/3 dados) correcto en ambas |  |  |
| `Daño total` muestra `defendibles/directos` cuando aplica |  |  |
| Costos siguen `Reiatsu / Energía` |  |  |

---

## Escenario C — 2v2 con target policy y cola

**Objetivo:** validar colapsables y metadata por grupo.

| Check | Resultado (Sí/No) | Evidencia |
|---|---|---|
| Línea de `target asignado` existe y responde al toggle `Target` |  |  |
| Línea de `operación ofensiva` responde al toggle `Operación ofensiva` |  |  |
| Línea de `Daño en cola 2v2` responde al toggle `Cola 2v2` |  |  |
| Con toggles cerrados, la vista principal queda limpia |  |  |
| Con toggles abiertos, se ve detalle completo |  |  |

---

## Escenario D — defensa IA con `force_strong`

**Objetivo:** validar el fix crítico de trazabilidad defensiva.

| Check | Resultado (Sí/No) | Evidencia |
|---|---|---|
| HUD/panel indica modo forzado `force_strong` |  |  |
| Log defensivo muestra línea canónica de `Defensa Fuerte` |  |  |
| No queda solo la operación sin técnica visible |  |  |
| Costos defensivos muestran `Reiatsu / Energía` |  |  |

---

## Protocolo de ejecución recomendado

1. Ejecutar escenarios en orden A → D.
2. Capturar evidencia mínima por escenario (captura o log textual).
3. Completar tabla en el momento (evitar memoria posterior).
4. Si hay un “No”, crear ticket de bloqueo con:
   - escenario,
   - check fallido,
   - evidencia,
   - módulo probable.

---

## Cierre de Fase 7

Se considera **aprobada** cuando:

- Todos los checks de A/B/C/D están en “Sí”.
- No hay bloqueantes abiertos vinculados a este checklist.
- El resultado queda archivado junto al commit/PR de cierre.

