# Phase 5 Implementation — Módulos del hub (mínimo viable real)

Fecha: 2026-04-04
Alcance implementado: F5-C, F5-P, F5-E, F5-A, F5-D, F5-B

---

## F5-C — Clases

Estado: ✅ Implementado.

- Lección 1 ahora muestra progreso `X/7` basado en checks.
- Se mantiene el marcado por sublección (1.1–1.7).
- Se añadió acción `Finalizar Lección 1` habilitada cuando están los 7 checks activos.

Resultado:
- Lección 1 queda operativa con estado de completitud basado en checks académicos.

---

## F5-P — Práctica

Estado: ✅ Implementado.

- Se creó `tl_practice_mode_screen`.
- Permite modo libre configurable: `letters`, `words`, `phrases`.
- Al iniciar práctica, entra a `typing_lab_start` con el modo seleccionado.

Resultado:
- El módulo Práctica deja de ser placeholder y ejecuta Typing Lab de forma configurable.

---

## F5-E — Exámenes

Estado: ✅ Implementado.

- Se creó `tl_exam_entry_screen` con un examen mínimo.
- Umbral de aprobación: `50` puntos.
- Flujo:
  1) fija modo de examen en `phrases`,
  2) ejecuta `typing_lab_start`,
  3) evalúa `typing_lab_state["total_score"]`.
- Si aprueba, marca check de examen:
  - `set_check("examenes", "exam_1", "attempt_1", True)`.

Resultado:
- Existe un examen funcional con criterio objetivo de aprobado/no aprobado.

---



---

## F5-A — Actividades

Estado: ✅ Implementado.

- Se creó `tl_activities_quest_screen`.
- Incluye 1 quest social funcional:
  - marca check `actividades/activity_1/quest_1`
  - aplica `+1` afinidad a Airi (`social_mission_success`).

Resultado:
- Actividades deja de ser placeholder y ya afecta el sistema social.

---

## F5-D — Diario

Estado: ✅ Implementado.

- Se creó `tl_diary_tabs_screen` con 2 tabs:
  - `Académico (checks)`
  - `Social (barras/corazón)`
- La tab social muestra afinidad y estado de romance por personaje sin mezclar lógica académica.

Resultado:
- Diario centraliza visualmente progreso académico y social en una sola pantalla.

---

## F5-B — Biblioteca

Estado: ✅ Implementado.

- Se creó `tl_library_index_screen` con fichas de:
  - Cursos (progreso y estado)
  - Personajes (afinidad + estado de desbloqueo)
- Estado de desbloqueo de personajes:
  - `Desbloqueado` si afinidad >= 1
  - `Bloqueado` si afinidad == 0

Resultado:
- Biblioteca deja de estar en construcción y entrega información útil del progreso.

---

## DoD Fase 5 (estado actualizado)

- Ningún módulo queda en “en construcción”: ✅
- MVP jugable de principio a fin: ✅ (flujo completo con módulos funcionales mínimos).
