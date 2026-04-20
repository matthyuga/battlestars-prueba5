# Fase 3 — Finalizador de combate dev (hardening + QA UX)

Fecha: 2026-04-20  
Estado: completada

## Objetivo
Cerrar la fase de herramienta dev con mejoras de seguridad operativa y observabilidad en UI.

## Cambios aplicados
1. **Guardrail de hotkeys**
   - `Ctrl+X` / `Ctrl+K+X` solo hacen toggle del panel si:
     - `config.developer == True`
     - `bs_saga_dev_admin_enabled == True`

2. **Panel dev mejorado**
   - Se agregó cierre por `Esc`.
   - Se muestra en panel el último cierre dev aplicado (`mode`, `ts`, `affected`).
   - Se añadió botón `Limpiar estado` para resetear la auditoría runtime.

3. **API auxiliar**
   - `bs_dev_clear_finish_combat_audit()` para limpiar `story_pilot_debug_last_finish_combat`.

## Resultado esperado
- Flujo dev más seguro y trazable.
- Menor riesgo de activación accidental de hotkeys fuera de contexto dev.
- Mejor visibilidad para QA sobre qué cierre forzado se ejecutó.

## Próximo paso
- Fase 4: smoke QA matriz completa (victory/defeat/draw + release guardrail checks).
