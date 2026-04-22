# Plan de fases — Rediseño de Inventario UI

Fecha: 2026-04-22  
Estado: **Fase 0, 1, 2, 3, 4 y 5 completadas**

## Fase 0 — Alineación UX/UI y alcance (completada)

Decisiones cerradas:
1. Adoptar layout en 3 paneles para inventario:
   - izquierda: categorías,
   - centro: listado,
   - derecha: detalle.
2. Mantener header actual (marca, territorio, oro, volver al lobby).
3. Mantener lógica de datos actual (`bs_saga_inventory_rows`) y enfocarse primero en estructura visual.
4. Dejar iconografía avanzada, rareza visual y filtros complejos para fases posteriores.

## Fase 1 — Estructura base (completada)

Implementado:
1. Panel izquierdo con categorías base (`Todos`, `Consumibles`, `Equipo`, `Materiales`, `Objetos clave`).
2. Panel central con listado seleccionable por categoría y estado de selección visible.
3. Panel derecho con detalle mínimo del ítem seleccionado (`item_id`, bucket, qty).
4. Estados vacíos por categoría sin ítems.

## Fase 2 — Tarjetas visuales del listado (completada)
- Las filas se convirtieron en cards con jerarquía visual (título, sublínea, acento por rareza y badge de cantidad).
- Se añadió estado seleccionado más claro por card.

## Fase 3 — Panel de detalle ampliado (completada)
- El panel derecho ahora muestra nombre legible, rareza, tier y descripción (`meta`) del ítem.
- Se incorporó resolución de metadatos del catálogo usando `item_id` (slug) para enriquecer el inventario.

## Fase 4 — Filtros y orden (completada)
- Se añadió selector de vista `Todos/Recientes`.
- Se añadió filtro por rareza (`all/common/rare/special/epic/legendary/mythic/infernal`).
- Se añadió ordenamiento por nombre, cantidad y rareza.

## Fase 5 — QA visual/funcional (completada)
- Se verificó la presencia de los nuevos controles y estados en `bs_saga_inventory_screen`.
- Se validó limpieza del patch (`git diff --check`).
- Se corrigió error runtime en orden por rareza (`NameError: _rar_order`) y se estabilizó el sizing visual de cards largas (amuletos).
- Queda pendiente QA manual in-engine para validar look final en runtime Ren'Py con contenido real.
