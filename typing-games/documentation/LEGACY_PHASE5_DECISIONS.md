# Typing Legends — Fase 5 (Legacy y limpieza)

Fecha: 2026-04-06

## Qué quedó en legacy

- Archivo: `typing-games/game/90_LEGACY_LESSONS_V1.rpy`
  - `screen tl_sublesson_intro_screen`
  - `screen tl_sublesson_content_screen`

## Por qué se movió a legacy

1. Era implementación inline previa en bootstrap (alto acoplamiento UI+flujo).
2. Se necesitaba preservar referencia histórica durante migración por fases.
3. El flujo nuevo ya está desacoplado por capas:
   - Data: `21_LESSONS_DB_V1.rpy`
   - Engine: `30_LESSON_ENGINE_V1.rpy`
   - Router: `31_LESSON_ROUTER_V1.rpy`
   - Visual: `41_LESSON_SCENES_V1.rpy`

## Regla operativa

- No reutilizar screens de legacy en flujo activo.
- Cualquier mejora nueva de lecciones se hace solo en capas nuevas.
- Legacy se mantiene únicamente como referencia hasta cierre de migración.

