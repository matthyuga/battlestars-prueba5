# FASE4_ECONOMIA_Y_META_PROGRESION_V1

Fecha: 2026-04-06  
Estado: Plan de ejecución (listo para implementar)

## 1) Meta

Integrar oro, estrellas y recompensas al resultado de combate con una fórmula clara, auditable y balanceable.

---

## 2) Alcance funcional (Fase 4)

### 2.1 Oro por duelo libre según tier

Definir banda mínima/máxima por tier para `duelo`:

| Tier | Oro mínimo | Oro máximo |
|---|---:|---:|
| C | 10 | 100 |
| B | 50 | 500 |
| A | 100 | 1,000 |
| S | 500 | 10,000 |
| SS | 1,000 | 15,000 |
| SSS | 5,000 | 25,000 |
| IV | 10,000 | 50,000 |

### 2.2 Multiplicadores por desempeño

La recompensa base se ajusta por factores de desempeño:

1. `eff_ec_ep` (eficiencia de gasto EC/EP)
2. `eff_damage` (daño efectivo)
3. `eff_block` (bloqueo efectivo)
4. `eff_survival` (HP restante / supervivencia)

Rango recomendado inicial por factor: **0.85 a 1.15**.

### 2.3 Variación aleatoria controlada

Aplicar factor aleatorio acotado:
- `rng_factor` en rango recomendado **0.95 a 1.05** (v1)
- Semilla registrada para replay QA.

### 2.4 Integración de estrellas

Casos incluidos:
- Conversión por duplicados de personaje.
- Compra en tienda con costos por tier.
- Registro de fuente de estrellas (`source_type`).

`source_type` sugeridos:
- `duplicate_conversion`
- `tower_reward`
- `event_reward`
- `shop_adjustment`

---

## 3) Fórmula base auditable (v1)

### 3.1 Componentes

- `gold_band_min`, `gold_band_max` (por tier)
- `perf_multiplier = eff_ec_ep * eff_damage * eff_block * eff_survival`
- `rng_factor`

### 3.2 Cálculo sugerido

1. `gold_base = midpoint(gold_band_min, gold_band_max)`
2. `gold_perf = gold_base * perf_multiplier`
3. `gold_final = clamp(gold_perf * rng_factor, gold_band_min, gold_band_max)`
4. `gold_final = round(gold_final)`

### 3.3 Restricciones

- Ninguna recompensa negativa.
- Clamp obligatorio por banda de tier.
- Versionar fórmula: `gold_formula_version = v1`.

---

## 4) Reporte post-battle (auditoría)

Campos obligatorios en reporte:
- `battle_id`
- `mode`
- `tier_context`
- `gold_band_min`
- `gold_band_max`
- `gold_base`
- `eff_ec_ep`
- `eff_damage`
- `eff_block`
- `eff_survival`
- `perf_multiplier`
- `rng_factor`
- `gold_final`
- `gold_formula_version`
- `stars_delta`
- `stars_source[]`

Objetivo: cualquier reward debe poder recalcularse offline para QA.

---

## 5) Control de inflación (QA)

### 5.1 Métricas mínimas (20-30 corridas)

- `avg_gold_per_battle` por tier
- `p95_gold_per_battle` por tier
- `stars_earned_per_hour`
- `shop_purchase_rate`
- `duplicate_to_star_ratio`

### 5.2 Alertas de inflación

Activar alerta si ocurre alguno:
1. `p95_gold_per_battle` excede +20% del objetivo de tier.
2. Tiempo a primer desbloqueo S/SS cae por debajo del umbral definido.
3. Crecimiento de estrellas/hora rompe banda esperada de progresión.

---

## 6) Criterios de salida Fase 4

1. Fórmula auditable en reportes de post-battle.
2. No hay inflación extrema en 20-30 corridas QA.

Criterios QA adicionales:
- Recalcular recompensas desde logs produce mismo `gold_final`.
- Conversión de duplicados registra fuente y valor de estrellas correctamente.
- Cambiar semilla de RNG altera resultado dentro de banda permitida.

---

## 7) Checklist de implementación

- [ ] Implementar bandas de oro por tier (duelo libre).
- [ ] Implementar cálculo de `perf_multiplier`.
- [ ] Integrar `rng_factor` controlado y seed de auditoría.
- [ ] Integrar estrellas (duplicados + compras).
- [ ] Exponer reporte post-battle con campos auditables.
- [ ] Ejecutar 20-30 corridas QA y evaluar inflación.

---

## 8) Entregables de Fase 4

1. `documentation/FASE4_ECONOMIA_Y_META_PROGRESION_V1.md` (este documento)
2. `documentation/TABLA_FORMULA_ORO_DESEMPENO_V1.md` (baseline + política de boosts por modo)
3. `documentation/CHECKLIST_QA_FASE4_ECONOMIA_V1.md` (pendiente)

---

## 9) Nota de alcance (actualización 2026-04-12)

Para evitar inflación y subida acelerada de cuenta en el modo de entrada:

- **Duelo Libre**:
  - mantener foco en oro;
  - aplicar boost de oro por tier de cuenta (tabla conservadora);
  - **no aplicar boost de EXP** en esta etapa.

- **Torneo / Torre del Cielo**:
  - habilitar boost de EXP por tier de cuenta;
  - sujeto a gates de entrada del modo (ticket/plantilla propia).
