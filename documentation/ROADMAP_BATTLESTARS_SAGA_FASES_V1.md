# Battlestars Saga — Roadmap por fases y pasos (v1)

Fecha: 2026-04-06  
Estado: En ejecución (Fase 0 iniciada)

---

## Objetivo

Implementar Battlestars Saga por fases controladas, priorizando estabilidad del núcleo de combate y evitando sobrecargar el sistema con demasiados ítems/reglas al inicio.

Avance actual:
- ✅ Definido roadmap por fases.
- ✅ Iniciada Fase 0 con contratos base de inventario, reglas de consumo/durabilidad y recompensas.
- ✅ Definido plan detallado de ejecución para Fase 1 (inventario MVP fuera de combate).

---

## Fase 0 — Contrato base + documentación (obligatoria)

**Meta:** definir un contrato único de datos para inventario, consumibles, equipables y recompensas, de forma que UI y runtime trabajen con la misma estructura.

### 0.1 Contrato canónico (Inventory Contract v1)

Definir en documentación y luego en código las entidades mínimas:

1. `item_catalog`
   - `item_id`
   - `item_type`: `consumable | equipable | amulet | tattoo`
   - `subtype`: `hp_potion | ec_potion | ep_potion | durability_potion | atk_buff | def_buff | stat_buff | ring | necklace | ...`
   - `rarity`
   - `tier_requirement`
   - `max_stack`
   - `durability_max` (si aplica)
   - `effects[]`

2. `inventory_profile`
   - `owner_id`
   - `items_owned{ item_id -> qty }`
   - `equipped_slots{ slot_id -> item_instance_id }`
   - `tattoo_slot`
   - `loadouts[]`

3. `combat_inventory_snapshot`
   - `battle_id`
   - `allowed_items[]`
   - `turn_usage_tracker`
   - `remaining_durability`
   - `run_bound_flags` (si viene de Torre)

4. `consumption_rules`
   - límites por turno (ej. 1 por tipo/color)
   - restricciones por modo
   - prioridad de resolución de efectos

5. `reward_payload`
   - `gold`
   - `stars`
   - `items`
   - `tickets`
   - `characters`

### 0.2 Reglas mínimas documentadas (sin excepción)

- Consumibles por turno:
  - Máximo 1 por tipo/color en el mismo turno.
  - No repetir la misma clase/color en el mismo turno.
- Equipables:
  - Dan bonus mientras estén equipados y tengan durabilidad > 0 (si aplica).
- Tatuajes:
  - 1 por personaje.
  - Efecto pasivo permanente (sin durabilidad).
- Amuletos raros:
  - Durabilidad inicial 3 usos.

### 0.3 Documentación a dejar en esta fase

1. `documentation/ROADMAP_BATTLESTARS_SAGA_FASES_V1.md` (este archivo)
2. `documentation/CONTRATO_INVENTARIO_BATTLESTARS_V1.md`
3. `documentation/REGLAS_CONSUMIBLES_Y_DURABILIDAD_V1.md`
4. `documentation/CONTRATO_RECOMPENSAS_ORO_ESTRELLAS_ITEMS_V1.md`

### 0.4 Criterio de salida Fase 0

- Contrato revisado y firmado (SSOT).
- Casos borde documentados (doble uso, item agotado, durabilidad 0, snapshot de combate).
- Checklist QA de contrato aprobado.

---

## Fase 1 — Inventario MVP (fuera de combate)

**Meta:** tener inventario funcional en lobby/perfil con equipamiento básico y carga de presets.

### 1.1 Alcance

- Alta/baja de ítems del inventario.
- Equipamiento en slots MVP (reducidos para estabilidad).
- 3 presets de configuración por personaje:
  - Balanceado
  - Ofensivo
  - Defensivo

### 1.2 Slots MVP recomendados

- 2 anillos
- 1 diadema
- 1 collar
- 2 brazaletes
- 1 tatuaje

### 1.3 Criterio de salida Fase 1

- Equipar/desequipar sin inconsistencias.
- Guardar/cargar 3 presets estable.
- Validación de tier/rareza funcionando.

---

## Fase 2 — Inventario en combate + consumibles base

**Meta:** habilitar uso real de ítems en batalla con reglas estrictas de consumo.

### 2.1 Alcance

- Snapshot de inventario al iniciar combate.
- Uso de pociones de recurso:
  - HP / EC / EP / Durabilidad (25/35/50 por color)
- Validaciones por turno:
  - 1 por tipo/color
  - bloqueo de duplicado en turno

### 2.2 Criterio de salida Fase 2

- No se puede explotar consumo por spam.
- El tracker por turno resetea correctamente al cambiar turno.
- Eventos de uso quedan logueados para QA.

---

## Fase 3 — Consumibles avanzados + amuletos raros

**Meta:** añadir profundidad táctica sin romper balance base.

### 3.1 Alcance

- Pociones de ataque/defensa por técnica (25/35/50).
- Pociones de stats para Torre (duración combate/run según regla).
- Amuletos raros (3 usos):
  - espejo reflectante
  - cilindro mágico
  - espada sagrada
  - daga maldita
  - daga envenenada

### 3.2 Criterio de salida Fase 3

- Orden de aplicación de efectos definido y estable.
- Tooltips y logs muestran efecto aplicado y duración restante.

---

## Fase 4 — Economía y meta-progresión

**Meta:** integrar oro/estrellas/recompensas con resultados de combate.

### 4.1 Alcance

- Oro por duelo libre según tier con banda mínima/máxima.
- Multiplicadores por desempeño:
  - eficiencia de gasto EC/EP
  - daño efectivo
  - bloqueo efectivo
  - supervivencia (HP restante)
- Variación aleatoria controlada.
- Integración de estrellas (duplicados y compras).

### 4.2 Criterio de salida Fase 4

- Fórmula auditable en reportes de post-battle.
- No hay inflación extrema en 20-30 corridas QA.

---

## Fase 5 — Torre del Cielo (MVP jugable)

**Meta:** corrida completa de Torre en tiers bajos con recompensas mixtas.

### 5.1 Alcance

- Bloques C/B (A opcional según estabilidad).
- Buffs temporales de run.
- Personajes temporales de run y reglas iniciales de permanencia.
- Tickets de torneo C/B/A como loot raro.

### 5.2 Criterio de salida Fase 5

- Run completa sin bloqueos.
- Recompensas aplicadas correctamente al salir de Torre.

---

## Fase 6 — Rotación de personajes + expansión de slots

**Meta:** activar contenido vivo y ampliar complejidad de equipamiento.

### 6.1 Alcance

- Rotación semanal de personajes libres.
- Distinción clara entre “libre temporal” y “desbloqueado permanente”.
- Expansión progresiva de slots (pendientes/tobilleras/cinturón/anillos extra).

### 6.2 Criterio de salida Fase 6

- Rotación estable por temporada.
- Métricas de adopción y conversión de desbloqueos positivas.

---

## Riesgos transversales y mitigación

1. **Complejidad temprana alta**
   - Mitigar con alcance MVP por fase y feature flags.

2. **Power creep por ítems/buffs**
   - Mitigar con caps, escalado de costo y telemetría temprana.

3. **Conflictos de reglas en combate**
   - Mitigar con contrato único + orden de resolución explícito.

---

## Próximos entregables recomendados

1. `CONTRATO_INVENTARIO_BATTLESTARS_V1.md` (detalle técnico de campos + ejemplos JSON)
2. `CHECKLIST_QA_INVENTARIO_Y_CONSUMO_V1.md`
3. `TABLA_FORMULA_ORO_DESEMPENO_V1.md`
4. `POLITICA_ROTACION_PERSONAJES_V1.md`
