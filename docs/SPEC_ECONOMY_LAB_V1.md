# SPEC — Economy Lab (EXP/Oro + Boosts + Desempeño) v1

Fecha: 2026-04-12  
Estado: DEFINE + PLAN (listo para implementación incremental)

---

## 1) Objetivo

Crear una herramienta interna simple (primero CLI, luego opcional UI web) para:

1. Simular recompensas de **oro** y **EXP** según:
   - tier de cuenta,
   - modo (`duelo_libre`, `torneo`, `torre`),
   - factores de desempeño,
   - boosts por tier definidos en documentación.
2. Comparar escenarios:
   - **normal** (sin boost),
   - **con boost por tier**.
3. Mostrar tablas y reportes para balance:
   - resultado por escenario,
   - sensibilidad por desempeño,
   - acumulado por N combates.

---

## 2) Fuentes de verdad (v1)

### 2.1 Oro por tier (bandas y fórmula base)
- `documentation/TABLA_FORMULA_ORO_DESEMPENO_V1.md`
- `documentation/FASE4_ECONOMIA_Y_META_PROGRESION_V1.md`

### 2.2 Política de boosts por modo (decisión vigente)
- Duelo Libre: boost de **oro** por tier de cuenta.
- Torneo/Torre: boost de **EXP** por tier de cuenta.
- Duelo Libre: sin boost de EXP en esta etapa.

### 2.3 Factores de desempeño
- `eff_ec_ep`, `eff_damage`, `eff_block`, `eff_survival`
- rango recomendado inicial: 0.85–1.15
- `rng_factor`: 0.95–1.05

---

## 3) Alcance funcional

## MVP (obligatorio)

1. Entrada:
   - `mode`
   - `account_tier`
   - `base_exp`
   - `gold_min`, `gold_max` (o lookup por tier)
   - `eff_*`
   - `rng_factor`
   - `is_victory`
   - `repetition_count`

2. Cálculo:
   - `gold_final` (normal y con boost)
   - `exp_final` (normal y con boost por política de modo)

3. Salida:
   - tabla textual por escenario
   - JSON exportable para QA/auditoría
   - resumen de delta porcentual entre escenarios

## Fase 2 (opcional)

- UI web local (panel simple) con:
  - sliders de desempeño,
  - selector de tier/modo,
  - gráfico de barras por escenario,
  - gráfico radar para desempeño.

---

## 4) Reglas de cálculo (v1)

## Oro

1. `gold_base = midpoint(min, max)`
2. `gold_base_boosted = gold_base * tier_gold_boost(mode, account_tier)`
3. `perf_multiplier = eff_ec_ep * eff_damage * eff_block * eff_survival`
4. `gold_raw = gold_base_or_boosted * perf_multiplier * rng_factor`
5. `gold_final = clamp(round(gold_raw), min, max)`

## EXP

1. `exp_base` definido por entrada/fórmula base del modo
2. `exp_base_boosted = exp_base * tier_exp_boost(mode, account_tier)`
3. aplicar multiplicadores de resultado/riesgo/antiabuso según runtime vigente
4. `exp_final = max(0, round(exp_raw))`

---

## 5) Tablas de boosts v1

## Oro (Duelo Libre)

| Tier | Boost |
|---|---:|
| C | x1.00 |
| B | x1.05 |
| A | x1.10 |
| S | x1.16 |
| SS | x1.23 |
| SSS | x1.31 |
| IV | x1.40 |

## EXP (Torneo/Torre)

| Tier | Boost |
|---|---:|
| C | x1.00 |
| B | x1.03 |
| A | x1.06 |
| S | x1.10 |
| SS | x1.14 |
| SSS | x1.19 |
| IV | x1.25 |

---

## 6) Diseño técnico sugerido

## Opción A (rápida) — Python CLI

- Archivo: `tools/economy_lab.py`
- Librerías: estándar (`argparse`, `json`, `csv`, `statistics`)
- Ventaja: cero dependencia visual, ideal para QA batch.

## Opción B (visual) — App local ligera

- Backend pequeño Python (FastAPI/Flask) o Node.
- Frontend simple (HTML + Chart.js) para barras/radar.
- Recomendado después del CLI.

---

## 7) Tareas (PLAN)

1. Definir contratos de input/output del simulador (JSON schema simple).
2. Implementar lookup de bandas por tier y boosts por modo.
3. Implementar función de cálculo `simulate_reward(...)`.
4. Agregar runner por lotes para 20/50/100 combates simulados.
5. Exportar reporte JSON/CSV.
6. (Opcional) montar UI web local con gráficos.

---

## 8) Criterios de aceptación

1. Para el mismo input, el resultado es determinístico si `rng_factor` está fijo.
2. `gold_final` nunca sale fuera de la banda `[min, max]`.
3. Duelo Libre:
   - aplica boost de oro,
   - no aplica boost de EXP.
4. Torneo/Torre:
   - aplica boost de EXP,
   - respeta antiabuso configurado.
5. El reporte incluye desglose de multiplicadores y valores intermedios.

---

## 9) Riesgos y mitigación

1. **Inflación de oro**  
   Mitigación: mantener clamp por banda + QA con p95 por tier.

2. **Subida de cuenta demasiado rápida**  
   Mitigación: boost EXP solo Torneo/Torre en v1.

3. **Desalineación entre docs y runtime**  
   Mitigación: fijar `economy_formula_version` y registrar en reportes.

---

## 10) Próximo paso sugerido

Implementar primero **CLI MVP** (`tools/economy_lab.py`) y validar con 30 simulaciones por tier/modo antes de abrir UI visual.

---

## 11) Avance actual (2026-04-12)

Estado de Módulo A (CLI):
- [x] Simulación single-run y batch.
- [x] Comparación normal vs policy_boost.
- [x] Export JSON/CSV.
- [x] Preset de bandas por tier (`--tier-band`).
- [x] Métricas agregadas (`min/p50/p95/max`) en consola y JSON.

Pendiente recomendado para cierre operativo:
- [x] Añadir ejemplos de comandos en un README corto de `tools/`.
- [x] Definir datasets de escenarios QA (casual/normal/hardcore) para corrida automática.

---

## 12) Congelación de baseline por versión

Se incorpora runner operativo:
- `tools/run_economy_baseline.py`

Objetivo:
1. Ejecutar suite completa.
2. Ejecutar escenarios individuales.
3. Guardar artefactos JSON/CSV por versión en carpeta dedicada.
4. Persistir `manifest.json` para trazabilidad.

Comparación entre versiones:
- `tools/compare_economy_baselines.py`
- Métricas foco v1: `gold_final_policy.{p50,p95}` y `exp_final_policy.{p50,p95}` por escenario.

---

## 13) Inicio Módulo B (v0)

Se agrega dashboard mínimo:
- `tools/economy_dashboard.py`

Entrada:
1. `suite.json` (baseline congelado)
2. `diff.json` (opcional, comparador v1)

Salida:
- HTML estático con:
  - tabla p50/p95 por escenario,
  - barras simples por escenario,
  - tabla de deltas old/new por métrica en diff.

---

## 14) Automatización y CI

Automatización ligera:
- `Makefile` con targets:
  - `economy-smoke`
  - `economy-freeze`
  - `economy-compare`
  - `economy-dashboard`
  - `economy-report`

Integración CI:
- `.github/workflows/economy-tools.yml`
- Pipeline:
  1. compile smoke,
  2. freeze A/B,
  3. compare A vs B,
  4. build dashboard.
