# Comparativa de fórmulas — Condición HP y Recompensas

Fecha: 2026-04-18

## Objetivo
Tener en un solo documento las **dos fórmulas actuales** que hoy conviven en el proyecto y una **tercera fórmula propuesta** para comparar impacto en balance (especialmente con `x1..x5` de condición HP).

---

## Fórmula actual #1 (legacy panel RPG, sin factor HP)

> Referencia: `compute_exp_oro_reward(...)` del panel RPG legacy.

### Ecuación

- `EXP = base_exp * m_risk_exp * m_result_exp * m_perf_exp * m_anti`
- `ORO = base_oro * m_risk_oro * m_result_oro * m_perf_oro * m_anti`

Donde:
- `m_perf_exp = 0.70 + 0.02 * stars`
- `m_perf_oro = 0.80 + 0.01 * stars`
- `m_result_exp = 1.00` si victoria, `0.70` si no victoria
- `m_result_oro = 1.00` si victoria, `0.50` si no victoria
- `m_risk_*` depende de `delta_register`
- `m_anti` depende de repetición

### Característica clave
- **No tiene multiplicador HP (`x1..x5`)**. La condición HP no altera directamente el payout en esta fórmula.

---

## Fórmula actual #2 (simulador battle_end, con factor HP lineal)

> Referencia: `compute_actor_reward(...)` del simulador de progresión.

### Ecuación

- `EXP = base_exp * m_risk_exp * m_result_exp * m_perf_exp * m_anti * m_multi * m_hp`
- `ORO = base_oro * m_risk_oro * m_result_oro * m_perf_oro * m_anti * m_multi * m_hp`

Donde:
- `m_hp = clamp(hp_reward_multiplier, 1, 5)`
- `m_multi = clamp(sqrt(enemies/allies), 0.85, 1.35)`
- Resultado por outcome:
  - victoria: `m_result_exp=1.00`, `m_result_oro=1.00`
  - empate: `m_result_exp=0.85`, `m_result_oro=0.75`
  - derrota: `m_result_exp=0.70`, `m_result_oro=0.50`

### Característica clave
- El factor HP es **lineal y fuerte**:
  - `x1 => m_hp=1`
  - `x5 => m_hp=5`
- Eso significa que, a igualdad de todo lo demás, `x5` paga **5 veces** que `x1`.

---

## Fórmula propuesta #3 (riesgo visible, crecimiento HP controlado)

### Diseño buscado
1. Mantener lectura simple para jugador: `x1..x5` sigue siendo relevante.
2. Evitar inflación severa de economía por linealidad extrema (`x5 = 5x reward`).
3. Separar claramente **HP de combate** y **reward económico**.

### Ecuaciones propuestas

#### A) HP efectivo de duelo (se mantiene lineal)

- `HP_duelo = HP_base * x_hp`
- con `x_hp ∈ {1,2,3,4,5}`

Esto preserva exactamente tu regla: **`x5 = HP base * 5`**.

#### B) Recompensas (EXP/ORO) con escala HP suavizada

- `m_hp_exp = 1 + 0.35 * (x_hp - 1)`
- `m_hp_oro = 1 + 0.30 * (x_hp - 1)`

- `EXP_raw = base_exp * m_risk_exp * m_result_exp * m_perf_exp * m_anti * m_multi * m_hp_exp`
- `ORO_raw = base_oro * m_risk_oro * m_result_oro * m_perf_oro * m_anti * m_multi * m_hp_oro`

- `EXP_final = clamp(round(EXP_raw), floor_exp, cap_exp)`
- `ORO_final = clamp(round(ORO_raw), floor_oro, cap_oro)`

Con:
- `floor_exp = 0` (o mínimo de diseño por modo)
- `floor_oro = 0` (o mínimo de diseño por modo)
- `cap_exp = round(base_exp * 4.0)`
- `cap_oro = round(base_oro * 3.5)`

### Lectura rápida del factor HP propuesto

| x_hp | m_hp_exp | m_hp_oro |
|---|---:|---:|
| x1 | 1.00 | 1.00 |
| x2 | 1.35 | 1.30 |
| x3 | 1.70 | 1.60 |
| x4 | 2.05 | 1.90 |
| x5 | 2.40 | 2.20 |

---

## Comparativa numérica (escenario neutro)

Supuestos para comparar solo el efecto HP:
- `base_exp=100`, `base_oro=60`
- `m_risk = 1`, `m_result = 1`, `m_perf = 1`, `m_anti = 1`, `m_multi = 1`

| Modelo | x1 (EXP/ORO) | x5 (EXP/ORO) | Relación x5 vs x1 |
|---|---:|---:|---:|
| Actual #1 (legacy) | 100 / 60 | 100 / 60 | 1.0x |
| Actual #2 (sim actual) | 100 / 60 | 500 / 300 | 5.0x |
| Propuesta #3 | 100 / 60 | 240 / 132 | 2.4x EXP / 2.2x ORO |

---

## Recomendación práctica

1. **Mantener HP lineal en combate** (`x5 = HP*5`) porque es claro para UX.
2. Migrar rewards al esquema propuesto #3 para evitar inflación y seguir premiando riesgo.
3. Aplicar por modo (`duel_free`, `tournament`, `tower`) con cap/floor diferentes.
4. Registrar auditoría por `match_id/reward_event_id` para evitar doble pago.

---

## Notas de implementación sugerida

- La propuesta #3 puede entrar sin romper contratos si se agrega como preset nuevo, por ejemplo:
  - `preset = "medium_v3_hp_soft"`
- Así se puede comparar `v2` vs `v3` en QA con misma semilla y mismos actores.
