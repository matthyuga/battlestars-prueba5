# Mapa general de parámetros — Economía EXP/Oro (v1)

Fecha: 2026-04-19

## Objetivo
Centralizar en una sola hoja todos los parámetros que hoy ajustan (directa o indirectamente) la recompensa de **EXP/Oro** por batalla, para facilitar balance y QA.

---

## 1) ¿Existe documentación de las 6 estrellas de desempeño?

Sí. Documentos recomendados:

1. `docs/GUIA_BALANCE_EXP_ORO_ESTRELLAS_V1.md`
   - Explica estrellas 0..30 y base EXP/Oro por estrellas.
2. `docs/PLANILLA_EXP_ORO_DESEMPENO_V1.md`
   - Fórmulas por ΔR + resultado + desempeño + antiabuso.
3. `docs/BLUEPRINT_LAB_PROGRESION_CONTRATO_SIMULADOR_V1.md`
   - Contrato técnico del simulador, con las 6 categorías.

Las 6 categorías actuales del runtime son:
- ofensiva
- defensiva
- control
- eficiencia
- tecnica
- impacto

---

## 2) Pipeline real de recompensa post-combate (actual)

Flujo simplificado:

1. `battle_end` arma `runtime` con resultado, HP, multipliers y estado de actor.
2. `sim_run_battle_end_simulation(runtime)` calcula rewards por actor.
3. `sim_apply_simulation_rewards_to_runtime(pack)` aplica al runtime.
4. Bridge a cuenta/lobby: `bs_saga_gain_account_rewards(exp, oro)` para que se refleje en UI Hub.

---

## 3) Factores que ajustan EXP/Oro en combate (simulador C10)

## 3.1 Estrellas (desempeño)

- Cada categoría se clamp a `0..5`.
- `stars_total = sum(6 categorías)` clamp `0..30`.

### Base por preset `medium_v2`
- `EXP_base = 35 + 3.5 * stars_total`
- `ORO_base = 15 + 2.0 * stars_total`

> Nota: en `medium_v2`, el multiplicador de desempeño explícito queda en `1.0` porque el efecto ya está absorbido en la base por estrellas.

## 3.2 Resultado del combate

- Victoria: `result_exp = 1.00`, `result_oro = 1.00`
- Empate: `result_exp = 0.85`, `result_oro = 0.75`
- Derrota: `result_exp = 0.70`, `result_oro = 0.50`

## 3.3 Riesgo por diferencia de registros (ΔR)

- Se calcula `delta_register` contra promedio de rivales.
- Luego aplica tabla `SIM_RISK_EXP_TABLE` y `SIM_RISK_ORO_TABLE`.

## 3.4 Multi-factor por tamaño de equipos

- Fórmula: `sqrt(enemies / allies)`
- Clamp: `0.85 .. 1.35`

## 3.5 Multiplicador HP (x1..x5)

- Clamp: `1..5`
- Multiplica linealmente EXP y Oro en la fórmula actual.

## 3.6 Antiabuso por repetición

- `repetition_count=1` -> `1.00`
- `=2` -> `0.60`
- `=3` -> `0.30`
- `>=4` -> `0.10`

## 3.7 Elegibilidad de actor

- Si `eligible_rewards = false`, no se otorgan rewards de combate.

---

## 4) Fórmula consolidada actual (combat sim)

Con actor elegible:

- `EXP = EXP_base(stars) * risk_exp(ΔR) * result_exp * perf_exp * anti * multi * hp_mult`
- `ORO = ORO_base(stars) * risk_oro(ΔR) * result_oro * perf_oro * anti * multi * hp_mult`

En preset `medium_v2`:
- `perf_exp = 1.0`
- `perf_oro = 1.0`

---

## 5) Factores de economía fuera del cálculo de combate

Estos no recalculan el reward del combate, pero afectan progresión/economía global:

## 5.1 Aplicación a cuenta (lobby)

- `bs_saga_gain_account_rewards(exp_gain, gold_gain)`:
  - suma oro a cuenta,
  - suma EXP y resuelve level-up,
  - recalcula `exp_to_next`.

## 5.2 Curva de EXP para subir nivel

- `exp_to_next(level) = round(100 * 1.12^(level-1))`
- Esto hace que niveles altos pidan mucha EXP.

## 5.3 Tool DEV semirandom

Parámetros:
- `bs_saga_dev_gain_exp_base`
- `bs_saga_dev_gain_gold_base`
- `bs_saga_dev_gain_variance_pct`
- `bs_saga_dev_gain_runs`

Regla del tool DEV:
- se fuerza `gold >= exp * 1.15` por duelo simulado.

> Importante: esta regla hoy está en el tool DEV, no en toda la fórmula de combate base.

## 5.4 Estimador de duelos

- `bs_saga_estimate_duels_to_targets(target_exp, target_gold)`
- Usa expectativas por duelo basadas en los parámetros DEV, no el simulador completo con todos los multiplicadores de batalla real.

---

## 6) ¿Qué NO está como factor explícito en la fórmula actual?

A día de hoy, no hay multiplicador explícito directo por:
- daño total infligido,
- daño recibido,
- tiempo de combate,
- cumplimiento de objetivos de misión.

Estos factores podrían mapearse a estrellas o agregarse como nuevo multiplicador.

---

## 7) Checklist de balance rápido (operativo)

1. Confirmar preset activo (`medium_v2` u otro).
2. Confirmar rango esperado de `stars_total` en partidas reales (no solo QA).
3. Auditar distribución de `delta_register` en matchmaking real.
4. Medir payout medio por modo (1v1, 2v2, etc.) con y sin HP x3/x5.
5. Validar que oro/exp cumplan objetivo de diseño por etapa de progresión.
6. Revisar curva `exp_to_next` en niveles altos y decidir si migrar a curva por tramo/tier.

---

## 8) Sugerencia de uso de este documento

- Usar esta hoja como “mapa maestro”.
- Usar `GUIA_BALANCE_EXP_ORO_ESTRELLAS_V1.md` para el detalle matemático de estrellas.
- Usar `comparativa_formulas_condicion_hp_y_recompensas.md` para decisiones de rediseño HP/reward.
