# MVP Data Contract — Phase 0 (Sakura Sunshine Academy)

Fecha: 2026-04-04
Alcance: Consolidación técnica para integrar progreso académico por checks, afinidad por barras y romance por corazón fragmentado.

---

## F0-T1 — Inventario de rutas de assets usadas en scripts

### 1) Rutas de fondos/escenas usadas en el bootstrap
Definidas en `typing-games/game/10_SAKURA_BOOTSTRAP_V1.rpy` vía `tl_asset(...)`:

- `images/tl/portal_main.jpg` (menú Typing Legends)
- `images/tl/sakura_gate.jpg` (puerta Sakura)
- `images/tl/sakura_hallway.jpg` (pasillo / hub / registro)
- `images/tl/sakura_classroom.jpg` (aula lecciones)
- `images/tl/tm_lesson_slide_01.png` (slide de apoyo Typing Master)

### 2) Rutas reales de imágenes del proyecto (estado actual)
Ubicadas en `typing-games/game/images`:

- `images/typing-games-menu.jpg`
- `images/sakura-sunshine/sakura-sunshine-academy-entrada.jpg`
- `images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg`
- `images/sakura-sunshine/sakura-sunshine-academy-salon.jpg`
- `images/sakura-sunshine/sakura_intro.jpg`
- `images/epic-spells/reinos.png`
- `images/epic-spells/place-holder-1.png`

### 3) Rutas GUI para sistemas sociales
Ubicadas en `typing-games/game/gui`:

- Afinidad (barra): `gui/barra-progreso/c0.png` a `gui/barra-progreso/c10.png`
- Romance (corazón): `gui/corazon/p0.png` a `gui/corazon/p25.png`

> Estado confirmado en repo: `gui/corazon/p0.png` a `gui/corazon/p25.png`.

---


## F0-T4 — IDs estables de personajes (cerrados)

Los IDs de personaje quedan fijados en `snake_case` y en minúscula para evitar drift entre scripts/UI/guardado.

### Lista oficial (13)

- Estudiantes: `airi`, `momoka`, `rinka`, `sora`, `aki`, `ren`, `tetsu`
- Profesores: `misaki`, `ayame`, `kaoru`, `haru`, `yuto`, `masato`

Reglas de ID:
- No usar espacios ni mayúsculas.
- El `character_id` nunca depende del texto mostrado al jugador.
- Si cambia el nombre de display, el ID se conserva.

---

## F0-T5 — Naming de estados visuales (cerrado)

## 1) Barra de afinidad
- Convención: `c{n}.png`
- Rango válido: `c0..c10`
- Estados totales: 11
- Piso: `c0`
- Techo: `c10`

## 2) Corazón de romance
- Convención: `p{n}.png`
- Rango válido: `p0..p25`
- Estados totales: 26
- Piso: `p0`
- Techo: `p25`

Reglas de validación:
- Si un estado no existe en disco, aplicar fallback al más cercano válido (preferencia: clamp a piso/techo).
- Toda lógica de render usa clamp antes de resolver la ruta del archivo.

---

## F0-T2 — Estructura de datos persistente

Se define un estado persistente mínimo en `store` (Ren'Py) para separar claramente académico/social/romance.

## 1) Progreso académico (checks)

`academic_checks: dict[str, dict[str, bool]]`

Propuesta de clave jerárquica:

- Nivel 1 (módulo): `clases`, `practica`, `examenes`, `actividades`, `diario`, `biblioteca`
- Nivel 2 (item): IDs de lecciones/sublecciones/tareas, por ejemplo:
  - `lesson_1_1_intro`: `true/false`
  - `lesson_1_2_home_row`: `true/false`

Reglas:
- Solo estados booleanos (check/uncheck).
- No se usan barras para progreso académico.

## 2) Afinidad por personaje (barras)

`affinity_points: dict[str, int]`

- Clave: `character_id` estable (`airi`, `momoka`, `rinka`, `sora`, `aki`, `ren`, `tetsu`, `misaki`, `ayame`, `kaoru`, `haru`, `yuto`, `masato`)
- Rango: `0..10` (clamp)
- Regla de incremento: `+1` por interacción o misión exitosa.
- Render visual: `c{affinity_points}.png` (`c0..c10`).

## 3) Romance por personaje (corazón)

`romance_points: dict[str, int]`

- Rango actual: `0..25` (clamp lógico)
- Render visual disponible: `p0..p25`.

Reglas de activación:
- Solo disponible si `tl_experience_mode == 3`.
- Solo para personaje romanceable bajo regla de elegibilidad (sexo opuesto según configuración elegida).

## 4) Flags de desbloqueo / gating

`social_flags: dict[str, bool | str | int]`

Claves mínimas sugeridas:

- `romance_mode_enabled: bool`
- `romance_eligible_<character_id>: bool`
- `romance_route_unlocked_<character_id>: bool`
- `romance_locked_reason_<character_id>: str`

---

## F0-T3 — Contrato de tipos y rangos (resumen operativo)

- `academic_checks[module_id][item_id] -> bool`
- `affinity_points[character_id] -> int (0..10)`
- `romance_points[character_id] -> int (0..25)`
- `social_flags[key] -> bool|str|int`

Operaciones núcleo:

- `set_check(module_id, item_id, value=True)`
- `add_affinity(character_id, amount=1)`
- `add_romance(character_id, amount=1)`
- `is_romance_enabled(character_id, player_mode, player_gender)`

Reglas de consistencia:

1. Académico (checks) nunca muta barras ni corazón.
2. Afinidad siempre está disponible y acotada a 0..10.
3. Romance solo muta en modo 3 y con elegibilidad verdadera.
4. Todas las mutaciones aplican clamp para evitar overflow.

---

## Criterios de aceptación de Fase 0

1. Existe un único documento de contrato (este archivo) versionado.
2. Equipos de UI/script comparten los mismos IDs y rangos.
3. El avance académico queda formalmente separado de la afinidad/romance.
4. Pisos y techos visuales quedan cerrados sin ambigüedad (`c0..c10`, `p0..p25`).
