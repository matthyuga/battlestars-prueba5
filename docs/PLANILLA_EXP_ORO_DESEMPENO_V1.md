# Planilla v1 — EXP/Oro por diferencia de registros + desempeño (30 estrellas)

Fecha: 2026-03-24  
Estado: borrador avanzado para validación de balance.

## 1) Propósito

Definir una base clara para recompensas de combate (EXP y Oro) que combine:

1. Diferencia de registros entre combatientes.
2. Resultado del combate (ganar/perder).
3. Desempeño medido en 6 parámetros (0–30 estrellas).
4. Anti-abuso por repetición/ventanas.

---

## 2) Contexto del sistema

- Nivel máximo: 500.
- 1 registro = 10 niveles.
- La economía debe premiar riesgo sin romperse por farmeo de rivales débiles.

---

## 3) Variables

- `Rj`: registro del jugador.
- `Rr`: registro del rival.
- `ΔR = Rr - Rj`.
- `BaseEXP`: valor base de EXP según tier/zona.
- `BaseOro`: valor base de Oro según tier/zona.
- `S`: estrellas totales de desempeño (0–30).
- `M_antiabuso`: multiplicador de control por repetición/ventana.

---

## 4) Multiplicadores por diferencia de registros

## 4.1 EXP (más sensible al riesgo)

| ΔR | M_riesgo_exp |
|---:|---:|
| <= -5 | 0.15 |
| -4 | 0.25 |
| -3 | 0.40 |
| -2 | 0.60 |
| -1 | 0.82 |
| 0 | 1.00 |
| +1 | 1.25 |
| +2 | 1.55 |
| +3 | 1.90 |
| +4 | 2.30 |
| >= +5 | 2.80 (cap) |

## 4.2 Oro (más conservador)

| ΔR | M_riesgo_oro |
|---:|---:|
| <= -5 | 0.25 |
| -4 | 0.40 |
| -3 | 0.55 |
| -2 | 0.72 |
| -1 | 0.88 |
| 0 | 1.00 |
| +1 | 1.12 |
| +2 | 1.28 |
| +3 | 1.45 |
| +4 | 1.65 |
| >= +5 | 1.85 (cap) |

---

## 5) Resultado del combate

### EXP
- Victoria: `M_resultado_exp = 1.00`
- Derrota: `M_resultado_exp = 0.70`

### Oro
- Victoria: `M_resultado_oro = 1.00`
- Derrota: `M_resultado_oro = 0.50`

---

## 6) Desempeño 30 estrellas (0–5 por parámetro)

Parámetros propuestos:

1. Ofensiva
2. Defensa
3. Control
4. Eficiencia
5. Técnica
6. Impacto

Total: `S` (0–30)

### Multiplicador por desempeño

- EXP: `M_desempeño_exp = 0.70 + (0.02 * S)` → rango 0.70 a 1.30
- Oro: `M_desempeño_oro = 0.80 + (0.01 * S)` → rango 0.80 a 1.10

---

## 7) Fórmulas finales

### 7.1 EXP

`EXP_final = BaseEXP * M_riesgo_exp(ΔR) * M_resultado_exp * M_desempeño_exp(S) * M_antiabuso`

### 7.2 Oro

`Oro_final = BaseOro * M_riesgo_oro(ΔR) * M_resultado_oro * M_desempeño_oro(S) * M_antiabuso`

---

## 8) Anti-abuso (v1 recomendado)

## 8.1 Repetición del mismo rival (ventana 24h)

- 1ª vez: `M_antiabuso = 1.00`
- 2ª vez: `M_antiabuso = 0.60`
- 3ª vez: `M_antiabuso = 0.30`
- 4ª+ vez: `M_antiabuso = 0.10`

## 8.2 Cap diario de oro por modo (placeholder)

- PvE normal: cap diario configurable (ej. 3,000–5,000)
- PvP: cap diario configurable (ej. 2,000–4,000)

> Ajustar con telemetría cuando exista mercado de ítems.

---

## 9) Ejemplos rápidos

Supuestos:

- `BaseEXP = 100`
- `BaseOro = 60`
- `S = 22` estrellas
- `M_desempeño_exp = 1.14`
- `M_desempeño_oro = 1.02`
- `M_antiabuso = 1.00`

### A) Mismo registro (ΔR=0), victoria

- `EXP = 100 * 1.00 * 1.00 * 1.14 * 1.00 = 114`
- `Oro = 60 * 1.00 * 1.00 * 1.02 * 1.00 = 61.2`

### B) Rival +3 registros (ΔR=+3), victoria

- `EXP = 100 * 1.90 * 1.00 * 1.14 * 1.00 = 216.6`
- `Oro = 60 * 1.45 * 1.00 * 1.02 * 1.00 = 88.74`

### C) Rival -3 registros (ΔR=-3), victoria

- `EXP = 100 * 0.40 * 1.00 * 1.14 * 1.00 = 45.6`
- `Oro = 60 * 0.55 * 1.00 * 1.02 * 1.00 = 33.66`

### D) Rival +3 registros (ΔR=+3), derrota

- `EXP = 100 * 1.90 * 0.70 * 1.14 * 1.00 = 151.62`
- `Oro = 60 * 1.45 * 0.50 * 1.02 * 1.00 = 44.37`

### E) Rival +3 registros, victoria, 3ª repetición

- `M_antiabuso = 0.30`
- `EXP = 216.6 * 0.30 = 64.98`
- `Oro = 88.74 * 0.30 = 26.622`

---

## 10) Placeholder económico de Oro (hasta tener mercado completo)

Objetivo: evitar inflación antes de activar sinks (craft, reparación, rerolls, etc.).

- Mínimo por combate válido: 20–30
- Promedio mismo registro: 50–80
- Alto riesgo + buen desempeño: 100–180
- Evitar >200 sostenido por combate hasta tener consumo de oro robusto.

---

## 11) Recomendación de implementación por fases

### Fase A
- Implementar fórmulas con constantes v1 (tablas de este documento).
- Activar logs por combate: ΔR, estrellas, multiplicadores, resultado final.

### Fase B
- Ajustar `BaseEXP/BaseOro` por tier y por modo.
- Afinar multiplicadores con datos reales de progresión.

### Fase C
- Introducir ajustes especiales por modo (PvE/PvP) solo si aparece desbalance persistente.

---

## 12) Checklist de validación rápida

1. ¿Ganar a rivales más fuertes acelera progreso, pero con cap?
2. ¿Farmear débiles da progreso muy bajo?
3. ¿Perder no deja al jugador en cero absoluto?
4. ¿El desempeño (estrellas) mejora recompensa sin dominarla?
5. ¿Anti-abuso baja de forma visible el farmeo repetitivo?

