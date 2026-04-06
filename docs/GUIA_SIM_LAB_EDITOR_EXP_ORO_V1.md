# Guía SIM Lab — Editor EXP/Oro/Estrellas (v1)

Fecha: 2026-03-31  
Estado: Activo (dev/QA)

---

## 1) ¿Qué es el SIM Lab?

El **SIM Lab** es una pantalla de desarrollo/QA para probar el simulador de progresión sin depender de un duelo real.

Permite:
- editar el request de simulación,
- configurar actores (tipo, nivel, registro, EXP/Oro, estrellas),
- ejecutar simulaciones,
- inspeccionar auditoría/idempotencia,
- revisar eventos mid-battle,
- correr smoke checklists,
- exportar JSON para QA (A/E/E5).

---

## 2) Rutas de acceso

### Opción A (rápida, recomendada dev)
- Menú principal → **Sim Lab Sandbox (Dev)**.

### Opción B
- Menú → **Help** → **SIM Lab (Dev)**.

> Nota: ambos accesos son dev-only (dependen de `config.developer`).

---

## 3) ¿Cómo usar el editor de EXP/Oro y filtros?

### Paso 1 — Definir contexto de simulación
En “Editor principal”:
- `mode`: 1v1 / 2v1 / 1v2 / 2v2 / custom
- `winner_team`: A / B / DRAW
- `event_type`: victory / defeat / draw / conditional_gain
- `source`: lab_manual / battle_end / mid_battle_event

### Paso 2 — Config de cálculo
En “Config”:
- `preset` (ej. medium_v2)
- `repetition_count`
- `multi_factor_enabled`
- `allow_mid_battle_grants`

### Paso 3 — Editar actores (núcleo del leveling)
En “Actores”:
- Tipo: `PLAYER`, `ALPHA`, `BETA`, `GAMMA`, `DELTA`
- Team: A/B
- Nivel (`level`) y registro (`register`)
- `exp_current`, `oro_current`
- estrellas por categoría (Of/Def/Ctl/Efi/Tec/Imp)
- flag de elegibilidad (`eligible_rewards`)

Con esto podés simular “campo de juego sin duelo” para balancear progresión.

### Paso 4 — Ejecutar y revisar
- Botón **Simular**
- Revisar:
  - “Resultados por actor”
  - “Auditoría + Idempotencia”
  - “D7 — QA Mid-battle inspector”

---

## 4) Flujos QA recomendados

## Flujo A — Balance manual rápido
1. Cargar fixture A/B/C.
2. Ajustar nivel/registro/estrellas.
3. Simular.
4. Verificar EXP/Oro final por actor.
5. Exportar `last result JSON`.

## Flujo B — Mid-battle / anti-duplicado
1. Ejecutar smoke checklist.
2. Revisar panel D7 de eventos.
3. Confirmar estados de idempotencia.

## Flujo C — Cierre Fase E
1. Exportar `fixtures E JSON`.
2. Exportar `E5 readiness JSON`.
3. Verificar gate `phaseE_e5_readiness_gate` en smoke.

---

## 5) Qué trae hoy (resumen funcional)

- Contrato + motor de simulación v1.
- Integración en `battle_end`.
- Mid-battle grants con guard rails e idempotencia.
- Reconciliación para evitar doble pago.
- SIM Lab con editor completo por actor.
- Inspector D7 para eventos mid-battle recientes.
- Smoke suites A/C/D/E4/E5.
- Exports QA:
  - Last result JSON
  - Fixtures A JSON
  - Fixtures E JSON
  - E5 readiness JSON

---

## 6) Limitaciones actuales

- No reemplaza netcode/matchmaking multiplayer real.
- Es herramienta dev/QA (no UX final de jugador).
- Requiere validación manual runtime para certificar cambios.

---

## 7) Siguiente paso sugerido

Con E5 instrumentado, ejecutar sesión de test manual guiada:
- smoke checklist,
- 2 fixtures E permitidos + 1 bloqueado,
- combate piloto hasta `battle_end` para validar no crash,
- export de evidencias JSON.

