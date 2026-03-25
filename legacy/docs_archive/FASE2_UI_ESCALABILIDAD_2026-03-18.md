# Fase 2 — Escalabilidad visual del pre-combate (2026-03-18)

## Estado
**Implementada (corte v1)** sobre la sala pre-combate.

---

## Cambios aplicados

1. **Compactación visual (~20%)**
   - Reducción de tamaño del panel principal y tipografías clave.
   - Objetivo: más técnicas visibles sin saturación.

2. **Paginación horizontal del catálogo**
   - Se agregó navegación por página (`◀` / `▶`) por categoría (`atk`, `def`).
   - Control por `precombat_catalog_page` + `precombat_catalog_per_page`.

3. **Vista con íconos + fallback simple**
   - Mapeo de íconos para técnicas en `game/gui/tech_buttons`.
   - Toggle de vista:
     - `Íconos` (si asset existe),
     - `Simple` (solo texto), útil para QA/fallback.

---

## Archivos

- `game/04I_PRECOMBAT_LOADOUT_SCREENV1.rpy`
- `docs/FASE2_UI_ESCALABILIDAD_2026-03-18.md`

---

## Criterio de salida para pasar a Fase 3

- Selector pre-combate mantiene usabilidad con listas más largas.
- No hay bloqueo funcional en equipar/quitar/validar/confirmar.
- Fallback simple disponible si falta asset o se desactiva vista con íconos.
