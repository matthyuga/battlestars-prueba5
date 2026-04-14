# P2-04 — Plan de pre-adaptadores para catálogos JSON canónicos (v0.2)

Fecha: 2026-04-14  
Estado: Aprobado para ejecución técnica

---

## 1) Objetivo

Reducir hardcode de catálogos en UI y preparar migración a fuente canónica JSON sin romper compatibilidad v0.1.

---

## 2) Alcance técnico

1. Crear capa de lectura (`catalog_adapter`) con fallback.
2. Soportar doble fuente temporal:
   - fuente A: estructura hardcode actual,
   - fuente B: JSON canónico externo.
3. Normalizar salida al mismo shape consumido por UI.

---

## 3) Contrato de salida del adaptador

Campos mínimos por ítem:
- `item_id`
- `name`
- `item_type`
- `rarity`
- `tier_requirement`
- `price_gold`
- `stackable`
- `max_stack`
- `meta`

Campos mínimos por héroe:
- `hero_id`
- `name`
- `franchise`
- `tier`
- `price_gold`
- `enabled_modes`

---

## 4) Plan por etapas

## Etapa A — Wrapper de lectura

- Introducir funciones `get_item_catalog()` y `get_hero_catalog()`.
- Mantener implementación actual como backend por defecto.

## Etapa B — Parser JSON canónico

- Añadir parser tolerante para archivos JSON de toolkit.
- Validar esquema mínimo y registrar errores de parseo.

## Etapa C — Switch por feature flag

- Flag sugerido: `catalog_json_adapter_enabled`.
- `false`: usa hardcode.
- `true`: usa JSON canónico, con fallback a hardcode en error.

## Etapa D — Telemetría y limpieza

- Registrar fuente usada (`hardcode|json`) en auditoría.
- Eliminar rutas legacy cuando JSON quede estable.

---

## 5) Riesgos y mitigaciones

1. Riesgo: JSON incompleto en runtime.  
   Mitigación: validación + fallback seguro.

2. Riesgo: divergencia de nombres/campos entre fuentes.  
   Mitigación: capa de normalización única.

3. Riesgo: regresión visual por datos faltantes.  
   Mitigación: placeholders + alertas en log.

---

## 6) Criterio de salida P2-04

1. Adaptador entrega shape único estable a UI.
2. Cambio de fuente vía flag funciona sin crashes.
3. Flujo compra héroe/ítem sigue operativo con ambas fuentes.

