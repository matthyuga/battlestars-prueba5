# Phase 3 Implementation — Afinidad social con barras (0..10)

Fecha: 2026-04-04
Alcance implementado: F3-T1, F3-T2, F3-T3, F3-T4, F3-T5, F3-T6

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
- En `Actividades` (hub) se añadió una ficha social con barras y acciones de prueba para disparar ambos eventos y mostrar el valor actualizado de afinidad.

---

## Notas

- Las barras quedan reservadas exclusivamente a afinidad: helper `get_affinity_bar_image(character_id)` retorna `gui/barra-progreso/c{n}.png`.
- Inicialización segura en bootstrap: `_affinity_ensure_store()`.


---

## F3-T4 — Render visual con `c0..c10`

Estado: ✅ Implementado.

- Cada personaje renderiza su barra con `get_affinity_bar_image(character_id)`.
- El helper resuelve la ruta `gui/barra-progreso/c{n}.png` según afinidad actual clamp 0..10.

---

## F3-T5 — Pantalla de ficha social (lista de personajes + barra)

Estado: ✅ Implementado.

- Se añadió `tl_social_profile_screen`.
- Muestra lista completa de personajes y su barra de afinidad.
- Incluye acciones de prueba para sumar afinidad por evento (`+ Interacción`, `+ Misión`).

---

## F3-T6 — Tooltips “Afinidad actual X/10”

Estado: ✅ Implementado.

- Se incorporó tooltip dinámico por hover de barra usando variable de pantalla (`_aff_tip`).
- Mensaje mostrado: `Afinidad actual X / 10 (character_id)`.

---

## DoD Fase 3 (estado)

- Todos los personajes tienen barra funcional: ✅
- No hay mezcla con progreso académico: ✅ (checklist académico permanece en Diario; barras en Ficha social).
