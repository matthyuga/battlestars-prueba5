# Plan de fases — Catálogo de itens (split Pociones vs Stats Torre)

Fecha: 2026-04-22  
Estado: **Fase 0 completada · Fase 1 iniciada**

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

## Próximas fases

### Fase 2 — Orden de grupos y etiqueta visible
- Insertar `stats_torre` en el orden preferido de `consumibles`.
- Ajustar label amigable en panel izquierdo si aplica.

### Fase 3 — Limpieza del panel central
- Quitar descripción/meta de cada fila del listado central.
- Mantener nombre + precio en centro y descripción completa en panel derecho.

### Fase 4 — QA visual/funcional
- Verificar navegación por grupos, compra, filtros, búsqueda y no regresión del panel derecho.
