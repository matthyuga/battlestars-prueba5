# Plan de fases — Rediseño de Inventario UI

Fecha: 2026-04-22  
Estado: **Fase 0 completada · Fase 1 iniciada/completada (layout base)**

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

## Próximas fases

### Fase 2 — Tarjetas visuales del listado
- Convertir filas en cards con jerarquía visual más marcada.

### Fase 3 — Panel de detalle ampliado
- Añadir descripción útil, rareza/tier e indicadores visuales.

### Fase 4 — Filtros y orden
- Agregar filtros (todos/recientes/rareza) y ordenamiento.

### Fase 5 — QA visual/funcional
- Validar navegación, scroll, selección, rendimiento y no regresión.
