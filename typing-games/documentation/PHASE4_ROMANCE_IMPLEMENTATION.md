# Phase 4 Implementation — Romance opcional (modo 3 + elegibilidad)

Fecha: 2026-04-04
Alcance implementado: F4-T1, F4-T2, F4-T3

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
- El render de corazón/UI romance se conecta en la siguiente tarea de fase (F4-T4+).
