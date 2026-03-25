# Plan por fases — Implementación panel de asignación (Ren'Py v1)

Fecha: 2026-03-25  
UI stack: **Ren'Py únicamente**.

## Objetivo

Implementar un panel funcional y auditado para:

- seleccionar atributo principal,
- asignar puntos de stat por registro,
- administrar pool técnico,
- validar caps PvP/PvE,
- confirmar cambios de forma segura.

---

## Estado de avance

- Fase 0: completada.
- Fase 1: completada (ver `docs/FASE1_PANEL_RENPY_CORE_EJECUCION_2026-03-25.md`).
- Fase 2: completada (ver `docs/FASE2_PANEL_RENPY_UI_MINIMA_EJECUCION_2026-03-25.md`).
- Fase 3: completada (ver `docs/FASE3_PANEL_RENPY_INTEGRACION_PLANILLAS_2026-03-25.md`).
- Fase 4: completada (ver `docs/FASE4_PANEL_RENPY_RECOMPENSAS_EJECUCION_2026-03-25.md`).
- Fase 5: completada (ver `docs/FASE5_PANEL_RENPY_QA_FUNCIONAL_EJECUCION_2026-03-25.md`).
- Fase 6: pendiente.

---

## Fase 0 — Freeze de reglas (0.5 día)

### Tareas
- Aceptar contrato de datos/eventos `CONTRATO_PANEL_ASIGNACION_RENPY_V1.md`.
- Congelar reglas núcleo (sin cambios durante Fases 1–3).

### Salida
- “Reglas v1 congeladas” aprobadas.

### Bloqueantes
- Ninguna implementación arranca sin freeze.

---

## Fase 1 — Core de cálculo (1–2 días)

### Tareas
- Implementar funciones puras:
  - `compute_register`
  - `compute_pool_total`
  - `compute_stat_effects`
  - `compute_principal_bonus`
  - `compute_caps_for_register`
  - `compute_preview`
  - `validate_panel_state`

### QA de fase
- Tests de escritorio con 3 seeds (reg0/reg10/reg35).
- Verificar errores bloqueantes y casos límite.

### Salida
- Motor de cálculo estable sin dependencia de estilo/UI.

---

## Fase 2 — Pantalla Ren'Py mínima (2 días)

### Tareas
- Implementar Panel A (Identidad + Stats).
- Implementar Panel B (Principal + Pool técnico).
- Implementar Modal de confirmación.

### Reglas de UX mínimas
- Botón Confirmar deshabilitado si `is_valid=False`.
- Mostrar lista de errores de validación.
- Mostrar preview Antes/Después.

### Salida
- Flujo completo funcional end-to-end en estilo básico.

---

## Fase 3 — Integración de planillas (1–2 días)

### Tareas
- Conectar caps por registro y modo PvP/PvE.
- Conectar curvas de consumo por técnica/familia.
- Validar que números mostrados coincidan con docs oficiales.

### Salida
- UI con datos reales del diseño (sin mocks numéricos).

---

## Fase 4 — Persistencia + auditoría (1 día)

### Tareas
- Persistir confirmaciones de panel.
- Guardar snapshot before/after.
- Registrar cambios en log de auditoría.

### Salida
- Trazabilidad total de asignaciones.

---

## Fase 5 — QA funcional (1–2 días)

### Matriz mínima
- 10 casos felices
- 10 casos de error
- 10 casos de borde (caps, 4/5 buckets, reset, toggle pvp/pve)

### Criterio de salida
- 0 bugs críticos.
- 0 inconsistencias numéricas entre UI y motor.

---

## Backlog inmediato post-v1

1. Integración post-combate con desempeño 30 estrellas.
2. Respec con costos de economía.
3. Rediseño visual (ya sobre base funcional estable).

---

## Definición de Done (DoD)

Se considera cerrado cuando:

- Contrato v1 implementado sin desviaciones.
- Validaciones bloqueantes activas.
- Seeds reg0/reg10/reg35 pasan QA.
- Confirmación persiste datos y log.
- El panel funciona en Ren'Py sin dependencias web.
