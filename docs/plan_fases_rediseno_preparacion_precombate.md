# Plan de fases — Rediseño de Preparación y Pre-combate (Battlestars Saga)

Fecha de inicio: 2026-04-18
Estado general: **Fase 1 completada**

---

## 1) Objetivo
Reorganizar el flujo UX/UI del módulo de preparación para que el jugador recorra de forma clara:

1. Selección (héroe/equipo)
2. Configuración (técnicas/equipamiento/build/cfg)
3. Validación e inicio del duelo

Sin romper la lógica funcional actual de validación y lanzamiento de combate.

---

## 2) Fases planificadas

| Fase | Nombre | Estado | Resultado esperado |
|---|---|---|---|
| 0 | Baseline y contrato de no-regresión | ✅ Completada | Documentar estado actual y límites de cambio |
| 1 | Sala de preparación (selección + resumen) | ✅ Completada | Reducir sobrecarga visual en pantalla inicial |
| 2 | Pantalla Configurar héroe (tabs) | ⏳ Pendiente | Separar edición en bloques lógicos |
| 3 | Pre-combate orientado a validación | ⏳ Pendiente | Checklist y decisiones finales sin edición profunda |
| 4 | Consolidación de flujo y rutas | ⏳ Pendiente | Unificar navegación y eliminar redundancias |
| 5 | Pulido visual / jerarquía UI | ⏳ Pendiente | Mejor legibilidad, estados y CTA |

---

## 3) Fase 0 — Baseline y contrato de no-regresión (COMPLETADA)

### 3.1 Inventario de pantallas y rutas actuales
- `screen bs_saga_preparation_room_screen` (sala de preparación).
- `screen bs_saga_duel_staging_screen` (pre-combate / staging).
- `screen bs_saga_preparation_verify_screen` (verificación final).
- Rutas de labels activas:
  - `label bs_saga_preparacion` (selector de contexto room/staging),
  - `label bs_saga_preparation_verify`,
  - `label bs_saga_launch_prepared_duel`.

### 3.2 Contrato de no-regresión definido
Durante Fases 1–3 se mantiene intacto el núcleo de combate:
- `bs_saga_precombat_contract_validate()`
- `bs_saga_apply_preparation_for_duel()`
- flujo de `bs_saga_launch_prepared_duel` hacia `battle_start`

### 3.3 Baseline funcional observado
Sala de preparación actual contiene en la misma vista:
- roster/filtros/rotación,
- resumen de héroe + stats + tuning,
- modo técnico + asignación +25/-25,
- CFG,
- loadout + equipamiento,
- build,
- resumen + CTA a pre-combate.

Pre-combate actual contiene:
- roster rápido,
- checklist pre-duelo con bloqueantes/warnings,
- modo 1v1/2v2,
- rival aleatorio/manual,
- build duelo,
- CTA a verificación/inicio.

### 3.4 Criterio de salida Fase 0
✅ Existe documentación de:
- pantallas/rutas actuales,
- puntos de no-regresión,
- alcance por fase.

---

## 4) Fase 1 — Sala de preparación (COMPLETADA)

### 4.1 Cambios aplicados
- Se mantuvo la estructura base de dos paneles (roster izquierda + configuración derecha).
- El panel derecho pasó a **modo resumen**:
  - héroe/equipo/config/build,
  - tier + pool de duelo,
  - stats base (HP/EP/EC/durabilidad/cubre),
  - modo técnico + pool técnico usado/libre,
  - loadout resumido (x/6),
  - CTA de transición a pre-combate.
- Se removió de esta pantalla la edición detallada (técnicas +25/-25, inventario equipable completo y gestión detallada de slots), que queda diferida a Fase 2.

### 4.2 Criterio de salida Fase 1
✅ Sala de preparación enfocada en selección + resumen, sin “torre” de edición en el mismo scroll.

### 4.3 Próximo paso (Fase 2)
- Implementar pantalla dedicada de **Configurar héroe** con tabs:
  - Resumen
  - Técnicas
  - Equipamiento
  - Build
  - CFG
- Conectar navegación desde “Configurar héroe” y retorno a sala/pre-combate.

---

## 5) Registro de avance por fase
- 2026-04-18 — **Fase 0 completada** (baseline + contrato de no-regresión).
- 2026-04-18 — **Fase 1 completada** (sala resumida + edición detallada diferida a Fase 2).
