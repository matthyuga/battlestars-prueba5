# Fase 0 + Fase 1 — Finalizador de combate (dev)

Fecha: 2026-04-20  
Estado: completadas

## Fase 0 (definición)
- Keymap aprobado para invocación rápida: `Ctrl+X`.
- Guardrails definidos:
  - requiere `config.developer`.
  - requiere `bs_saga_dev_admin_enabled`.
- Política técnica definida:
  - finalizar siempre por ruta canónica `battle_end`.
  - sin bypass de simulación/aplicación de recompensas.

## Fase 1 (API canónica)
Se implementó la API `bs_dev_finish_combat(mode)` con soporte:
- `mode="victory"`
- `mode="defeat"`
- `mode="draw"`

### Comportamiento
- Fuerza KO del/los equipo(s) según modo usando estado de batalla cuando está disponible.
- Aplica fallback legacy si no hay APIs de estado.
- Registra auditoría en `story_pilot_debug_last_finish_combat`.
- Emite log dev en battle log.
- Cierra con `renpy.jump("battle_end")`.

### Compatibilidad
- `bs_dev_instant_victory()` ahora delega a `bs_dev_finish_combat("victory")`.
- Se expone hotkey `Ctrl+X` para cierre rápido por victoria dev.

## Próximo paso (Fase 2)
- Construir panel centrado superior (`Ctrl+X`) con botones:
  - Victoria
  - Derrota
  - Empate
  - Cerrar panel
