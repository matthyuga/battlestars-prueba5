# Phase 3 Implementation — Afinidad social con barras (0..10)

Fecha: 2026-04-04
Alcance implementado: F3-T1, F3-T2, F3-T3

---

## F3-T1 — `affinity_points` por personaje (default 0)

Estado: ✅ Implementado.

Se creó `default affinity_points = affinity_default_points()` con IDs estables de personajes y valor inicial `0`.

---

## F3-T2 — `add_affinity(character_id, +1)` con clamp 0..10

Estado: ✅ Implementado.

Se implementó:
- `_affinity_clamp()` con límites `0..10`.
- `_affinity_ensure_store()` para asegurar/migrar estructura en store.
- `add_affinity(character_id, amount=1)` con retorno del valor final.

---

## F3-T3 — Eventos que suman afinidad

Estado: ✅ Implementado.

Eventos definidos:
- `interaction_success` (+1)
- `social_mission_success` (+1)

Se implementó `award_affinity_event(character_id, event_key)` para aplicar estas reglas.

Integración de demo en flujo actual:
- En `Actividades` (hub) se añadió menú de prueba para disparar ambos eventos y mostrar valor actualizado de afinidad.

---

## Notas

- Las barras quedan reservadas exclusivamente a afinidad: helper `get_affinity_bar_image(character_id)` retorna `gui/barra-progreso/c{n}.png`.
- Inicialización segura en bootstrap: `_affinity_ensure_store()`.
