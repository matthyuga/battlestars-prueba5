# Bitácora SIM Lab + Simulador de Progresión

Fecha: 2026-04-06  
Estado: En curso (transición a flujo por pasos)

---

## 1) Contexto general

Se construyó un stack de simulación de progresión con:
- contrato v1 de request/result,
- cálculo de recompensas EXP/Oro/estrellas,
- idempotencia por `reward_event_id`,
- pipeline de eventos `mid_battle_event`,
- reconciliación con `battle_end`,
- UI de laboratorio (SIM Lab) para QA/dev,
- helpers de smoke/e2e y export JSON.

Objetivo final: tener un flujo de QA estable, reproducible y no invasivo para probar balance/progresión sin depender del duelo en runtime.

---

## 2) Estado funcional actual (resumen)

### Componente motor (10C)
- Contrato y validación base disponibles.
- `run_simulation` disponible y utilizable desde UI/runtime.
- Idempotencia y ledger mid-battle implementados.
- Reconciliación en cierre de combate implementada.
- Suites de pruebas y gates A/C/D/E disponibles (helpers runtime).

### Integración battle_end (04e)
- Integración con simulación en cierre de combate disponible.
- Se añadieron defensas para que errores de persist/apply no rompan el flujo principal (evidencia en reportes en store).

### UI SIM Lab (10D)
- Editor unificado disponible (modo actual “monolítico”).
- Paneles de resultados/auditoría/export/smoke disponibles.
- Inspector D7 para eventos mid-battle disponible.

### Menú/rutas (screens)
- Accesos dev al SIM Lab disponibles (main menu/help).

---

## 3) Problemas observados en QA (sesiones recientes)

1. **Crashes por sustitución de texto Ren'Py**
   - Causa: uso de patrones que Ren'Py interpreta como placeholders en runtime.
   - Mitigación aplicada en sesiones: se normalizaron varias líneas de texto dinámico.

2. **Comportamiento de input no deseado en SIM Lab**
   - Síntoma: clic en parámetros dispara navegación/menú/batalla en vez de ejecutar solo acción local.
   - Patrón coincide con herramientas previas (editor de puntos/pre-combate).

3. **Inestabilidad de contexto de pantalla**
   - Indicadores: necesidad de “destrabar” con F1 o apertura inesperada de menús.

---

## 4) Diagnóstico de diseño

El SIM Lab actual está resuelto como **pantalla única con demasiadas acciones activas simultáneamente**.

Consecuencias:
- mayor probabilidad de conflictos de contexto/input,
- validaciones dispersas,
- UX menos guiada para QA,
- mayor complejidad para aislar bugs de navegación.

Conclusión: conviene migrar a **flujo por pasos (wizard)** con bloqueos/confirmaciones por etapa.

---

## 5) Plan por pasos para continuar (próxima sesión)

## Paso 0 — Mantener compatibilidad
- Conservar `sim_lab_v1` como “Advanced/Legacy”.
- Implementar nuevo `sim_lab_wizard_v1` en paralelo.

## Paso 1 — Estado del wizard
- Crear estado explícito:
  - `sim_lab_wizard_step_v1` (1..4)
  - `sim_lab_wizard_step_confirmed_v1` (dict)
  - `sim_lab_wizard_errors_v1` (lista)
  - `sim_lab_wizard_snapshot_v1` (request por paso)

## Paso 2 — Wizard 1/4 (Contexto)
- Selección única de:
  - mode,
  - winner_team,
  - event_type,
  - source.
- Botón “Confirmar paso 1” bloqueado hasta completar requeridos.

## Paso 3 — Wizard 2/4 (Config)
- `preset`, `repetition_count`, toggles.
- Confirmación de paso con validación mínima.

## Paso 4 — Wizard 3/4 (Actores)
- Alta/edición de actores.
- Tipos: PLAYER/ALPHA/BETA/GAMMA/DELTA.
- Ajustes: nivel/registro/exp/oro/stars/elegibilidad.
- Confirmación de paso.

## Paso 5 — Wizard 4/4 (Ejecución QA)
- Simular, ver auditoría, correr smoke, exportar JSON.
- Botones de ejecución solo activos si pasos 1..3 están confirmados.

## Paso 6 — Navegación controlada
- `Back/Next`.
- Si se edita un paso confirmado, invalidar confirmaciones posteriores.

## Paso 7 — Rutas de entrada estables
- Ruta recomendada QA: abrir wizard (no pantalla legacy) desde menú dev.
- Mantener acceso legacy para debugging avanzado.

## Paso 8 — Criterios de aceptación (DoD)
- Clic en controles no abre menú/batalla.
- Confirmaciones por paso funcionan y bloquean correctamente.
- Simulación y export solo en paso final.
- Corridas de smoke visibles y reproducibles.

## Paso 9 — Cierre operacional
- Ejecutar checklist manual completo.
- Exportar evidencia (A/E/E5).
- Registrar issues abiertos y decisión go/no-go.

---

## 6) Checklist sugerido para arrancar próxima sesión

1. Definir alcance de Sprint “Wizard SIM Lab v1”.
2. Crear estados default del wizard y helpers de validación por paso.
3. Implementar solo Paso 1 y cablear confirmación.
4. Verificar que input no dispare navegación externa.
5. Avanzar progresivamente hasta Paso 4.

---

## 7) Notas de coordinación

- Priorizar estabilidad de interacción sobre nuevas features.
- Evitar cambios masivos en motor de cálculo mientras se estabiliza UX de laboratorio.
- Mantener trazabilidad de decisiones en esta bitácora y actualizarla al cierre de cada sesión.

