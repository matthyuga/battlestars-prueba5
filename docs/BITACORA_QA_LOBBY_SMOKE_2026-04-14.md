# Bitácora QA — Smoke Lobby/Combate (2026-04-14)

Fuente: validación manual en Ren'Py Launcher (usuario).

---

## 1) Estado por bloque A..G

- A) Precondiciones: PASS.
- B) Navegación: PASS (fluida).
- C) Economía lobby: PASS (compra héroes/ítems y reflejo en inventario).
- D) Pasaje a combate: PASS (flujo funcional tras fix de `ai_difficulty_hud`).
- E) Consumo en combate: PASS (consumo de recursos funcional).
- F) Integridad: PASS (sin divergencias bloqueantes reportadas en smoke actual).
- G) Global: PASS provisional para el alcance actual.

---

## 2) Incidencia crítica encontrada

### `Screen ai_difficulty_hud is not known`

Traza reportada:
- `game/04A_BATTLE_CHARACTER_SELECTV3.rpy` al ejecutar `show screen ai_difficulty_hud`.

Acción aplicada en esta iteración:
- se reintroduce `screen ai_difficulty_hud` con controles básicos de dificultad IA (`basic/intermediate/advanced`) y toggle de persistencia.

---

## 3) Hallazgos de UX/Producto (backlog)

1. Añadir pantalla de perfil de usuario con:
   - tier, nivel, oro, EXP detallada,
   - historial de combates,
   - top 3 héroes más usados (global/24h).
2. En lobby mantener barra de EXP resumida.
3. Reemplazar hardcode de roster Bleach por héroes del lobby adquirido/rotación.
4. Añadir panel de preparación pre-combate:
   - selección de héroe,
   - build/equipamiento,
   - chequeo de requisitos (tier/técnicas/pool).
5. Definir ciclo de rotación y reglas por modo (1v1/2v2, enemigo fijo/aleatorio).

---

## 4) Siguiente paso recomendado

1. Mantener smoke corto por cada cambio nuevo que toque selector o runtime de combate.
2. Priorizar backlog UX (perfil, preparación pre-combate, roster no-hardcodeado).
3. Abrir fase de hardening visual/datos con criterios de no-regresión ya aprobados.
