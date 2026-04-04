# Phase 4 Implementation — Romance opcional (modo 3 + elegibilidad)

Fecha: 2026-04-04
Alcance implementado: F4-T1, F4-T2, F4-T3, F4-T4, F4-T5, F4-T6

---

## F4-T1 — `is_romance_enabled(player_mode, player_gender, character_id)`

Estado: ✅ Implementado.

Reglas aplicadas:
- Solo habilita romance si `player_mode == 3`.
- Solo habilita romance si `player_gender` es `male` o `female`.
- Solo habilita romance con personaje de sexo opuesto (según mapa `ROMANCE_CHARACTER_GENDER`).

---

## F4-T2 — `romance_points` por personaje (default 0)

Estado: ✅ Implementado.

Se añadió:
- `romance_default_points()`
- `default romance_points = romance_default_points()`
- `_romance_ensure_store()` para inicialización/migración segura en saves.

---

## F4-T3 — `add_romance(character_id, +1)` con clamp 0..24

Estado: ✅ Implementado.

Se añadió:
- `add_romance(character_id, amount=1)`
- clamp por `_romance_clamp()` con rango `0..24` (hoy)
- helper `get_romance(character_id)` para lectura de estado actual

---

## Integración runtime

- El bootstrap inicializa también el store de romance en `tl_boot_start` mediante `_romance_ensure_store()`.
- El render de corazón/UI romance queda integrado en `tl_social_profile_screen`.


---

## F4-T4 — Agregar estado visual `p0` (corazón vacío)

Estado: ✅ Implementado (integración runtime).

- El sistema de render de corazón usa explícitamente rango visual `p0..p25`.
- `p0` queda como estado vacío en render para personajes con 0 puntos.

---

## F4-T5 — Renderizar corazón `p0..p25`

Estado: ✅ Implementado.

Se añadió helper:
- `get_romance_heart_image(character_id)`

Comportamiento:
- Toma `romance_points` actuales (0..24).
- Mapea visualmente a `p0..p25` para usar toda la secuencia gráfica.

---

## F4-T6 — Mensaje UI si romance bloqueado

Estado: ✅ Implementado.

Se añadió helper:
- `get_romance_lock_message(player_mode, player_gender, character_id)`

Mensajes:
- `Disponible solo en modo 3`
- `No elegible con configuración actual`

Integración:
- En `tl_social_profile_screen`, si el romance no está habilitado se muestra mensaje de bloqueo.
- Si está habilitado, se muestra corazón y botón `+ Romance`.

---

## DoD Fase 4 (estado)

- Romance solo aparece en modo 3: ✅
- Reglas de elegibilidad funcionan: ✅
- Corazón no rompe flujo de jugadores no-romance: ✅ (muestra mensajes de bloqueo en lugar de controles de romance).
