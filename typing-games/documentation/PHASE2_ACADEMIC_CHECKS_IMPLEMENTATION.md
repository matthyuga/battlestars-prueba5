# Phase 2 Implementation — Sistema académico por checks

Fecha: 2026-04-04
Alcance implementado: F2-T1, F2-T2, F2-T3, F2-T4, F2-T5, F2-T6

---

## F2-T1 — Estructura `academic_checks` (módulo > lección > sublección)

Estado: ✅ Implementado.

Se agregó un blueprint de checks académicos por módulo con estructura anidada:
- módulo (`clases`, `practica`, `examenes`, `actividades`, `diario`, `biblioteca`)
- lección (ej. `lesson_1`, `practice_1`)
- sublección/paso (ej. `1_1_intro`, `free_letters`, etc.)

También se incluyó normalización de alias para nombres con/sin tildes (`Práctica`, `Exámenes`) al resolver módulo.

---

## F2-T2 — Función `set_check(module, lesson, step, value=True)`

Estado: ✅ Implementado.

Comportamiento:
- Normaliza `module_id`.
- Asegura estructura existente en store (`_academic_ensure_store`).
- Marca/desmarca el check con booleano.
- Retorna valor final guardado.

---

## F2-T3 — Función `get_check_progress(module)`

Estado: ✅ Implementado.

Comportamiento:
- Devuelve avance por módulo en formato:
  - `done`
  - `total`
  - `ratio`
  - desglose por lección (`lessons`).

Integración UI:
- En el hub se muestra progreso académico del módulo actual como:
  - `Progreso académico (checks): X/Y`

---

## Notas de compatibilidad

- Se añadió migración suave para saves previos vía `_academic_ensure_store` (agrega claves faltantes sin romper datos existentes).
- El sistema académico queda separado de barras de afinidad/corazón de romance.


---

## F2-T4 — Integrar checks en “Clases” (Lección 1.1–1.7)

Estado: ✅ Implementado.

Integración aplicada:
- En `tl_lessons_mock_screen` se conectaron los 7 ítems de Lección 1 como `textbutton` que marcan check con `set_check(...)`.
- Cada sublección muestra `✓` cuando su check está activo.
- Se añadió acción rápida "Marcar todo Lección 1" para pruebas del flujo de progreso.

---

## F2-T5 — Vista en Diario (checklist académico)

Estado: ✅ Implementado.

Integración aplicada:
- Se creó `tl_diary_checklist_screen`.
- Muestra checklist académico por módulo/lección/sublección en formato de checks (`✓` / `□`).
- Se evita cualquier barra de progreso en esta vista (solo checks + conteos X/Y).

---

## F2-T6 — Persistencia en save/load

Estado: ✅ Implementado.

Soporte de persistencia:
- `default academic_checks = academic_default_checks()` permite guardar/cargar estado en save de Ren'Py.
- `_academic_ensure_store()` migra/agrega claves faltantes para compatibilidad con saves previos.
- Se invoca `_academic_ensure_store()` al entrar al bootstrap para garantizar estructura válida en runtime.
