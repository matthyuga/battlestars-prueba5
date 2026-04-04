# Phase 2 Implementation — Sistema académico por checks

Fecha: 2026-04-04
Alcance implementado: F2-T1, F2-T2, F2-T3

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
