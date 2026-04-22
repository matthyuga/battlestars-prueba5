# Plan de fases — Catálogo de itens (split Pociones vs Stats Torre)

Fecha: 2026-04-22  
Estado: **Fase 0, 1, 2 y 3 completadas**

## Fase 0 — Definición funcional (completada)

Decisiones cerradas:
1. Adoptar opción B: nueva subcategoría para pociones de stats de Torre del Cielo.
2. Mantener `pociones` para consumibles de duelo normal (HP/EP/EC/durabilidad).
3. Crear `stats_torre` para consumibles de stat temporal (`Solo Torre`).
4. La descripción de cada ítem seguirá visible en panel derecho; el panel central quedará sin texto descriptivo en fase posterior.

## Fase 1 — Split de datos (iniciada)

Objetivo:
- Separar el catálogo de `consumibles` en dos grupos claros para mejorar navegación y legibilidad.

Ejecución:
1. Mover filas `Solo Torre` desde `consumibles.groups.pociones` hacia `consumibles.groups.stats_torre`.
2. Mantener en `pociones` solo potions de uso general en duelo.
3. Reflejar el mismo split en el fallback embebido del schema para evitar divergencias cuando no cargue JSON externo.

## Fase 2 — Orden de grupos y etiqueta visible (completada)
- `stats_torre` se insertó en el orden preferido de `consumibles`.
- Se aplicó etiqueta visible amigable: `Stats (Torre del cielo)`.

## Fase 3 — Limpieza del panel central (completada)
- Se quitó la descripción/meta por fila en el panel central.
- El panel central conserva nombre + precio.
- La descripción completa permanece en panel derecho.

## Próxima fase

### Fase 4 — QA visual/funcional (pendiente)
- Verificar navegación por grupos, compra, filtros, búsqueda y no regresión del panel derecho.
