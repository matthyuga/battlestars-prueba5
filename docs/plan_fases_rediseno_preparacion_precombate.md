# Plan de fases — Rediseño de Preparación y Pre-combate (Battlestars Saga)

Fecha de inicio: 2026-04-18
Estado general: **Fase 5 completada**

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
| 2 | Pantalla Configurar héroe (tabs) | ✅ Completada | Separar edición en bloques lógicos |
| 3 | Pre-combate orientado a validación | ✅ Completada | Checklist y decisiones finales sin edición profunda |
| 4 | Consolidación de flujo y rutas | ✅ Completada | Navegación unificada y menos pasos duplicados |
| 5 | Pulido visual / jerarquía UI | ✅ Completada | Mejor legibilidad, jerarquía visual y CTA |

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

## 5) Fase 2 — Pantalla Configurar héroe (COMPLETADA)

### 5.1 Cambios aplicados
- Se creó la pantalla `bs_saga_hero_config_screen`.
- Se incorporaron tabs funcionales:
  - `Resumen`
  - `Técnicas`
  - `Equipamiento`
  - `Build`
  - `CFG`
- Se conectó la navegación desde la sala (`Configurar héroe`) hacia contexto `config`.
- Se conectó retorno a sala y avance a pre-combate desde la nueva pantalla.
- Se amplió el contexto de preparación a `room | config | staging`.

### 5.2 Criterio de salida Fase 2
✅ Existe una pantalla dedicada para edición detallada del héroe y la sala principal quedó enfocada en selección + resumen.

### 5.3 Próximo paso (Fase 3)
- Ajustar `Pre-combate` para que sea mayormente validación (checklist + decisiones finales), reduciendo edición profunda en esa vista.

---

## 6) Fase 3 — Pre-combate orientado a validación (COMPLETADA)

### 6.1 Cambios aplicados
- Se simplificó el panel izquierdo de `Pre-combate` para mostrar **resumen de entrada**:
  - héroe/tier/equipo,
  - modo/rival,
  - build/config,
  - pool y loadout equipado.
- Se retiró de esta vista la edición profunda de roster (elegir/equipo/quitar por fila).
- Se añadió CTA explícita para volver a la configuración detallada del héroe.
- Se mantuvo el panel derecho con checklist y opciones finales (modo, rival, build e iniciar).

### 6.2 Criterio de salida Fase 3
✅ Pre-combate enfocado en validación final + decisiones de entrada, sin mezclar edición profunda de selección.

### 6.3 Próximo paso (Fase 4)
- Consolidar rutas y limpiar redundancias entre `config`, `staging` y `verify`.
- Ajustar copy/acciones finales para minimizar pasos duplicados.

---

## 7) Registro de avance por fase
- 2026-04-18 — **Fase 0 completada** (baseline + contrato de no-regresión).
- 2026-04-18 — **Fase 1 completada** (sala resumida + edición detallada diferida a Fase 2).
- 2026-04-18 — **Fase 2 completada** (pantalla Configurar héroe con tabs + navegación de contexto).
- 2026-04-18 — **Fase 3 completada** (pre-combate centrado en validación y sin edición profunda de roster).
- 2026-04-18 — **Fase 4 completada** (staging y verify consolidados en una sola ruta principal para reducir pasos redundantes).
- 2026-04-18 — **Fase 5 completada** (pulido visual de estados/checklist/CTA y jerarquía UI entre sala, configuración y pre-combate).

---

## 8) Fase 4 — Consolidación de flujo y rutas (COMPLETADA)

### 8.1 Cambios aplicados
- Se consolidó la validación final dentro de `Pre-combate` para que el flujo principal sea:
  - `room` → `config` → `staging` → `iniciar duelo`.
- Se mantuvo `label bs_saga_preparation_verify` por compatibilidad, redirigiendo a `staging`.
- Se eliminaron duplicidades de CTA entre `staging` y `verify` en el flujo normal.

### 8.2 Criterio de salida Fase 4
✅ Navegación unificada sin paso obligatorio extra para verificar, manteniendo compatibilidad con rutas antiguas.

---

## 9) Fase 5 — Pulido visual / jerarquía UI (COMPLETADA)

### 9.1 Cambios aplicados
- Se reforzó la jerarquía visual en `Pre-combate` con:
  - estado general de validación (listo / warnings / bloqueado),
  - indicadores de bloqueantes y warnings más visibles,
  - separación clara entre checklist, decisiones de duelo y preparación de flags.
- Se priorizó el CTA principal (`Iniciar duelo`) dentro del mismo staging.
- Se añadieron mensajes contextuales para reducir ambigüedad de acciones y estado.

### 9.2 Criterio de salida Fase 5
✅ Flujo final más legible y directo, con validación y acción principal en una sola pantalla.

---

## 10) Fase 0 (Iteración UX v2) — Alineación aprobada

Fecha: 2026-04-18

Alineación cerrada con aprobación de producto para iniciar implementación:

1. **Modo técnico único en UI:** ocultar opción `Virgen` y operar solo en `Preconfig`.
2. **Paso configurable de asignación de puntos:** `25, 50, 100, 150, 200, 500, 1000`.
3. **Salida post-combate:** volver al lobby (no reiniciar al menú principal).

### Gate de avance
✅ **Fase 0 aprobada**. Lista para iniciar Fase 1 de implementación.
