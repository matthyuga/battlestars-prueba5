# Typing Legends — Fase 6 QA funcional

Fecha: 2026-04-06  
Ámbito: flujo activo de lecciones (`panel submódulos -> router -> scenes nuevas`)

## Checklist mínimo (resultado)

1. **Desde panel submódulos, 1.1 abre escena nueva.** ✅  
   Evidencia: `10_SAKURA_BOOTSTRAP_V1.rpy` delega a `tl_route_selected_sublesson`; el router abre `tl_lesson_intro_scene` para `intro_dialogue/1_1_intro`.

2. **Continuar avanza por tramos.** ✅  
   Evidencia: `tl_lesson_intro_scene` asigna `on_continue=SetVariable("tl_intro_page", min(... +1))` y `can_continue=lesson_can_advance(...)`.

3. **Avanzar solo habilita al último tramo.** ✅  
   Evidencia: `can_advance=(not lesson_can_advance(...))`.

4. **Atrás vuelve a panel.** ✅  
   Evidencia: `on_back=[SetVariable("tl_intro_page", 0), Return("back_class")]` y router/flow manejan `back_class`.

5. **`set_check("1_1_intro")` solo cuando `complete`.** ✅ (flujo activo)  
   Evidencia: router ejecuta `lesson_complete(...)` solo si `_result == "complete"`.

6. **1.2..1.7 abren placeholders sin error.** ✅  
   Evidencia: router envía casos no `intro_dialogue` a `tl_lesson_placeholder_scene`.

## Nota de alcance

- Existe una pantalla de QA/manual (`tl_lessons_mock_screen`) con botones de seteo directo de checks para pruebas técnicas; no forma parte del flujo académico activo de sublecciones.

