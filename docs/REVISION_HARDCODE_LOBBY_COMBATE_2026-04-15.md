# Revisión de hardcode — Lobby/Combate (2026-04-15)

Objetivo: identificar puntos hardcodeados que conviene revisar antes de continuar implementación.

---

## Resumen ejecutivo

Hallazgos principales:

1. **Fallbacks de roster y selección de combate hardcodeados** (IDs específicos tipo `Harribel/Grimmjow/Nel/Hollow`).
2. **Catálogo de ítems de la tienda embebido en código** como esquema local de fallback.
3. **Catálogo de técnicas/tiers y grupos UI embebidos** en funciones del Hub.
4. **Selector legacy 1v1/2v2 con menús y defaults hardcodeados** (mismo pool fijo de personajes).
5. **Dificultad IA con enum fija** (`basic/intermediate/advanced`) repetida en varios módulos.
6. **Panel DEV con valores rígidos** (`+50k oro`, `Lv 99`, `EXP 0`) embebidos en UI.

---

## Hallazgos detallados (por archivo)

## A) `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`

### A.1 Roster/combate con fallbacks fijos (alto impacto)
- Fallback de `combat_ready_ids` devuelve lista fija de héroes.
- Rotación, resolución de IDs y composición 2v2 usan defaults de héroes concretos.

Riesgo:
- Desacople entre progreso real del lobby y runtime de combate.
- Bloquea escalabilidad del roster cuando entren catálogos externos.

### A.2 Catálogo de ítems en código (alto impacto)
- `bs_saga_item_schema()` define un esquema completo local (consumibles, amuletos, materiales, etc.) con nombres/rarezas/tier/meta hardcodeados.

Riesgo:
- Difícil versionado de economía y balance.
- Cambios funcionales mezclados con cambios de texto/UI.

### A.3 Catálogo de técnicas y metadata de ayuda en código (medio/alto)
- `bs_saga_tech_catalog*` y llaves de tier/tipo están embebidas en funciones.

Riesgo:
- Duplicidad con datasets de combate y riesgo de drift entre HUD, ayuda y lógica real.

### A.4 Reglas/constantes UI embebidas (medio)
- Categorías de catálogo, orden preferido de grupos, defaults de filtros, etc., definidos inline.

Riesgo:
- Menor flexibilidad para iterar sin tocar runtime.

---

## B) `game/04A_BATTLE_CHARACTER_SELECTV3.rpy`

### B.1 Selector legacy con menú de personajes fijo (alto impacto)
- Defaults iniciales de `battle_player_id`/`battle_enemy_id` y menús 1v1 con nombres concretos.
- Flujo de selección mantiene ramas estáticas en lugar de consumir roster data-driven.

Riesgo:
- Multiplica deuda de mantenimiento mientras conviven lobby nuevo + selector legacy.

### B.2 Enum de dificultad IA rígida (medio)
- Nivel IA validado contra tupla fija y botones hardcodeados.

Riesgo:
- Si se agregan nuevos perfiles IA, hay que tocar varias capas manualmente.

---

## C) `game/03B_CHARACTER_DATABASE_V1.rpy`

### C.1 Dataset canónico de personajes embebido (medio/alto)
- `CHARACTER_DB` está declarado inline con lista extensa de personajes/tier/franquicia.

Riesgo:
- Fricción para curación de contenido, versionado y trazabilidad de cambios.

---

## D) `game/4/04D_AI_PLANS_COREV1.rpy`

### D.1 Dificultad IA por strings fijos (medio)
- `DEFAULT_AI_LEVEL` y validación de niveles con literales repetidos.

Riesgo:
- Acoplamiento entre UX y núcleo IA; poca extensibilidad para nuevos modos.

---

## Propuesta de priorización de revisión (antes de seguir features)

1. **P0 — Roster/combate data-driven completo**
   - eliminar fallbacks de héroes fijos en Hub/Preparación/2v2.
   - fuente única: catálogo/roster unificado (con fallback técnico acotado y observable).

2. **P0 — Extraer catálogo de ítems/técnicas a fuente de datos versionable**
   - mover esquema local a JSON/contrato canónico.
   - dejar en código solo parser/adaptador + validación.

3. **P1 — Retirar selector legacy hardcodeado**
   - enrutar selección 1v1/2v2 desde preparación data-driven.

4. **P1 — Centralizar enums/config globales**
   - dificultad IA, categorías de tienda, tiers visibles, defaults de filtros.

5. **P2 — Normalizar valores DEV**
   - `+50k/Lv99/EXP0` y toggles a config editable de entorno.

---

## Checklist de seguimiento rápido

- [ ] Inventariar todas las rutas con fallback de héroes fijos.
- [ ] Definir contrato único de roster para preparación + runtime.
- [ ] Extraer `item_schema` y `tech_catalog` a fuente externa.
- [ ] Reemplazar menú legacy de selección por flujo data-driven.
- [ ] Consolidar enum IA en un solo punto de verdad.
- [ ] Validar no-regresión Win7/Win10 tras cada bloque.

---

## Nota de alcance

Este documento cubre **hardcodes funcionales** en el frente lobby/combate.
No prioriza hardcodes puramente visuales (colores/espaciados) salvo que impacten flujo o mantenibilidad.
