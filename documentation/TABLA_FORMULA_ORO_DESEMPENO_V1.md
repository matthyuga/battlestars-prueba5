# TABLA_FORMULA_ORO_DESEMPENO_V1

Fecha: 2026-04-07  
Estado: Baseline de economía (Fase 4)

## 1) Objetivo

Definir la tabla de cálculo de oro por desempeño para Duelo Libre, con fórmula auditable y bandas por tier.

---

## 2) Bandas por tier

| Tier | Min | Max | Midpoint (base) |
|---|---:|---:|---:|
| C | 10 | 100 | 55 |
| B | 50 | 500 | 275 |
| A | 100 | 1,000 | 550 |
| S | 500 | 10,000 | 5,250 |
| SS | 1,000 | 15,000 | 8,000 |
| SSS | 5,000 | 25,000 | 15,000 |
| IV | 10,000 | 50,000 | 30,000 |

---

## 3) Factores de desempeño (v1)

Cada factor con rango recomendado 0.85–1.15:
- `eff_ec_ep`
- `eff_damage`
- `eff_block`
- `eff_survival`

Factor aleatorio controlado:
- `rng_factor`: 0.95–1.05

---

## 4) Fórmula v1

1. `gold_base = midpoint(min, max)`
2. `perf_multiplier = eff_ec_ep * eff_damage * eff_block * eff_survival`
3. `gold_perf = gold_base * perf_multiplier`
4. `gold_raw = gold_perf * rng_factor`
5. `gold_final = clamp(round(gold_raw), min, max)`

Restricciones:
- `gold_final >= 0`
- clamp obligatorio
- versionado: `gold_formula_version=v1`

---

## 5) Tabla de sensibilidad rápida (ejemplo)

Ejemplo Tier B (min 50, max 500, base 275):

| Escenario | eff_ec_ep | eff_damage | eff_block | eff_survival | rng | gold_final aprox |
|---|---:|---:|---:|---:|---:|---:|
| Bajo desempeño | 0.90 | 0.90 | 0.90 | 0.90 | 0.98 | 177 |
| Normal | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 275 |
| Alto desempeño | 1.10 | 1.10 | 1.05 | 1.10 | 1.02 | 396 |

---

## 6) Campos obligatorios en reporte

- `battle_id`
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

---

## 7) Validación QA (20-30 corridas)

- [ ] `p95_gold_per_battle` dentro de banda esperada
- [ ] `avg_gold_per_battle` consistente por tier
- [ ] No hay saltos anómalos por RNG
- [ ] Recalcular desde logs produce mismo `gold_final`
